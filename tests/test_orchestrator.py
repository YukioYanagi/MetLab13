from __future__ import annotations

import asyncio
import json
from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestrator.config import Settings
from orchestrator.models import SearchRoomsRequest
from orchestrator.service import HotelOrchestrator, TaskDispatchError


class FakeMessage:
    def __init__(self, payload: dict) -> None:
        self.data = json.dumps(payload).encode("utf-8")


class FakeNATSClient:
    def __init__(self, responses: list[object]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, dict, float]] = []
        self.drained = False

    async def request(self, subject: str, data: bytes, timeout: float):
        payload = json.loads(data.decode("utf-8"))
        self.calls.append((subject, payload, timeout))
        outcome = self.responses.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return FakeMessage(outcome)

    async def drain(self) -> None:
        self.drained = True


def make_settings(max_retries: int = 3) -> Settings:
    return Settings(
        nats_url="nats://localhost:4222",
        search_subject="hotel.rooms.search",
        request_timeout=0.1,
        max_retries=max_retries,
        log_dir="logs",
        log_level="INFO",
    )


def make_request() -> SearchRoomsRequest:
    return SearchRoomsRequest(
        request_id="req-test-001",
        city="Moscow",
        check_in=date(2026, 6, 12),
        check_out=date(2026, 6, 14),
        guests=2,
        rooms=1,
        max_price=220,
    )


def test_search_available_rooms_success() -> None:
    async def run() -> None:
        client = FakeNATSClient(
            [
                {
                    "request_id": "req-test-001",
                    "status": "success",
                    "agent_id": "search-agent-a",
                    "message": "available rooms found",
                    "available_rooms": [],
                    "handled_tasks": 1,
                }
            ]
        )
        orchestrator = HotelOrchestrator(settings=make_settings(), client=client)

        response = await orchestrator.search_available_rooms(make_request())

        assert response.request_id == "req-test-001"
        assert response.status == "success"
        assert orchestrator.metrics()["processed_tasks"] == 1
        assert len(client.calls) == 1

    asyncio.run(run())


def test_search_retries_after_timeout() -> None:
    async def run() -> None:
        client = FakeNATSClient(
            [
                asyncio.TimeoutError(),
                {
                    "request_id": "req-test-001",
                    "status": "success",
                    "agent_id": "search-agent-b",
                    "message": "available rooms found",
                    "available_rooms": [],
                    "handled_tasks": 2,
                },
            ]
        )
        orchestrator = HotelOrchestrator(settings=make_settings(), client=client)

        response = await orchestrator.search_available_rooms(make_request())

        assert response.agent_id == "search-agent-b"
        assert orchestrator.metrics()["retry_count"] == 1
        assert len(client.calls) == 2

    asyncio.run(run())


def test_search_fails_after_max_retries() -> None:
    async def run() -> None:
        client = FakeNATSClient(
            [
                asyncio.TimeoutError(),
                asyncio.TimeoutError(),
                asyncio.TimeoutError(),
            ]
        )
        orchestrator = HotelOrchestrator(settings=make_settings(max_retries=3), client=client)

        try:
            await orchestrator.search_available_rooms(make_request())
        except TaskDispatchError as exc:
            assert "failed after 3 attempts" in str(exc)
        else:
            raise AssertionError("TaskDispatchError was not raised")

        assert orchestrator.metrics()["failed_tasks"] == 1
        assert len(client.calls) == 3

    asyncio.run(run())


def test_close_drains_client() -> None:
    async def run() -> None:
        client = FakeNATSClient([])
        orchestrator = HotelOrchestrator(settings=make_settings(), client=client)

        await orchestrator.close()

        assert client.drained is True

    asyncio.run(run())
