from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(slots=True)
class Settings:
    nats_url: str
    search_subject: str
    request_timeout: float
    max_retries: int
    log_dir: str
    log_level: str


def load_settings() -> Settings:
    return Settings(
        nats_url=os.getenv("NATS_URL", "nats://localhost:4222"),
        search_subject=os.getenv("SEARCH_SUBJECT", "hotel.rooms.search"),
        request_timeout=float(os.getenv("REQUEST_TIMEOUT", "2.0")),
        max_retries=int(os.getenv("MAX_RETRIES", "3")),
        log_dir=os.getenv("LOG_DIR", "logs"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
