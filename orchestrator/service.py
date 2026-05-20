from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, TypeVar

from pydantic import BaseModel

from .config import Settings
from .models import SearchRoomsRequest, SearchRoomsResponse

ResponseModelT = TypeVar("ResponseModelT", bound=BaseModel)


class TaskDispatchError(RuntimeError):
    pass


class HotelOrchestrator:
    def __init__(
        self,
        settings: Settings,
        logger: logging.Logger | None = None,
        client: Any | None = None,
    ) -> None:
        self.settings = settings
        self.logger = logger or logging.getLogger("orchestrator")
        self._client = client
        self.processed_tasks = 0
        self.retry_count = 0
        self.failed_tasks = 0

    async def connect(self) -> None:
        if self._client is not None:
            return

        try:
            import nats
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Package 'nats-py' is not installed. Run 'python -m pip install -r requirements.txt'."
            ) from exc

        last_error: Exception | None = None
        for attempt in range(1, 6):
            try:
                self.logger.info(
                    "Connecting to NATS: url=%s attempt=%s/5",
                    self.settings.nats_url,
                    attempt,
                )
                self._client = await nats.connect(self.settings.nats_url)
                self.logger.info("Connected to NATS")
                return
            except Exception as exc:  # pragma: no cover - exercised only with real NATS
                last_error = exc
                self.logger.error("NATS connection failed: %s", exc)
                if attempt < 5:
                    await asyncio.sleep(2)

        raise TaskDispatchError("Could not connect to NATS") from last_error

    async def close(self) -> None:
        if self._client is None:
            return

        drain = getattr(self._client, "drain", None)
        if callable(drain):
            await drain()
        self._client = None

    async def search_available_rooms(self, request: SearchRoomsRequest) -> SearchRoomsResponse:
        payload = request.model_dump(mode="json")
        return await self._dispatch_with_retry(
            subject=self.settings.search_subject,
            payload=payload,
            response_model=SearchRoomsResponse,
        )

    def metrics(self) -> dict[str, int]:
        return {
            "processed_tasks": self.processed_tasks,
            "retry_count": self.retry_count,
            "failed_tasks": self.failed_tasks,
        }

    async def _dispatch_with_retry(
        self,
        subject: str,
        payload: dict[str, Any],
        response_model: type[ResponseModelT],
    ) -> ResponseModelT:
        if self._client is None:
            raise TaskDispatchError("Orchestrator is not connected to NATS")

        encoded_payload = json.dumps(payload).encode("utf-8")
        request_id = payload.get("request_id", "unknown")
        last_error: Exception | None = None

        for attempt in range(1, self.settings.max_retries + 1):
            try:
                self.logger.info(
                    "Dispatching task: subject=%s request_id=%s attempt=%s/%s",
                    subject,
                    request_id,
                    attempt,
                    self.settings.max_retries,
                )
                message = await self._client.request(
                    subject,
                    encoded_payload,
                    timeout=self.settings.request_timeout,
                )
                response_data = json.loads(message.data.decode("utf-8"))
                response = response_model.model_validate(response_data)
                self.processed_tasks += 1
                self.logger.info(
                    "Task completed: request_id=%s agent_id=%s status=%s",
                    response.request_id,
                    response.agent_id,
                    response.status,
                )
                return response
            except Exception as exc:
                last_error = exc
                is_timeout = isinstance(exc, asyncio.TimeoutError) or exc.__class__.__name__ == "TimeoutError"
                if is_timeout:
                    self.logger.error(
                        "Timeout waiting for response: request_id=%s attempt=%s/%s",
                        request_id,
                        attempt,
                        self.settings.max_retries,
                    )
                else:
                    self.logger.error(
                        "Task dispatch failed: request_id=%s attempt=%s/%s error=%s",
                        request_id,
                        attempt,
                        self.settings.max_retries,
                        exc,
                    )

                if attempt < self.settings.max_retries:
                    self.retry_count += 1
                    await asyncio.sleep(0.2 * attempt)

        self.failed_tasks += 1
        raise TaskDispatchError(
            f"Task {request_id} failed after {self.settings.max_retries} attempts"
        ) from last_error
