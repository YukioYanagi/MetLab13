from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request

from orchestrator.agent_catalog import AGENT_CATALOG
from orchestrator.config import load_settings
from orchestrator.logging_config import configure_logging
from orchestrator.models import SearchRoomsRequest, SearchRoomsResponse
from orchestrator.service import HotelOrchestrator, TaskDispatchError


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()
    api_logger = configure_logging("api", settings.log_dir, settings.log_level)
    orchestrator_logger = configure_logging("orchestrator", settings.log_dir, settings.log_level)

    orchestrator = HotelOrchestrator(settings=settings, logger=orchestrator_logger)
    await orchestrator.connect()

    app.state.api_logger = api_logger
    app.state.orchestrator = orchestrator
    api_logger.info("API started")

    try:
        yield
    finally:
        await orchestrator.close()
        api_logger.info("API stopped")


app = FastAPI(
    title="Hotel Booking Multi-Agent API",
    version="1.0.0",
    lifespan=lifespan,
)


def get_orchestrator(request: Request) -> HotelOrchestrator:
    return request.app.state.orchestrator


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/agents")
async def list_agents() -> list[dict]:
    return AGENT_CATALOG


@app.get("/metrics")
async def metrics(orchestrator: HotelOrchestrator = Depends(get_orchestrator)) -> dict[str, int]:
    return orchestrator.metrics()


@app.post("/search", response_model=SearchRoomsResponse)
async def search_rooms(
    payload: SearchRoomsRequest,
    orchestrator: HotelOrchestrator = Depends(get_orchestrator),
) -> SearchRoomsResponse:
    try:
        return await orchestrator.search_available_rooms(payload)
    except TaskDispatchError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
