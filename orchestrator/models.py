from __future__ import annotations

from datetime import date
from typing import List
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class RoomAvailability(BaseModel):
    hotel_id: str
    hotel_name: str
    city: str
    room_id: str
    room_type: str
    capacity: int
    price_per_night: float
    currency: str
    amenities: List[str]
    cancellation_to: str


class SearchRoomsRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    city: str
    check_in: date
    check_out: date
    guests: int = Field(default=1, gt=0)
    rooms: int = Field(default=1, gt=0)
    max_price: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_dates(self) -> "SearchRoomsRequest":
        if self.check_in >= self.check_out:
            raise ValueError("check_in must be earlier than check_out")
        if (self.check_out - self.check_in).days > 30:
            raise ValueError("stay must not exceed 30 nights")
        return self


class SearchRoomsResponse(BaseModel):
    request_id: str
    status: str
    agent_id: str
    message: str
    available_rooms: List[RoomAvailability]
    handled_tasks: int
