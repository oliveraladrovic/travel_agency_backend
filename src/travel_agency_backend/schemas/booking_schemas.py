from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime, date

from ..utils.enums import BookingStatus


class BookingCreate(BaseModel):
    departure_id: int
    seats_reserved: int = Field(..., ge=1, le=10)


class BookingOut(BaseModel):
    id: int
    departure_id: int
    seats_reserved: int
    price_per_seat_snapshot: Decimal
    total_price_snapshot: Decimal
    status: BookingStatus
    created_at: datetime
    updated_at: datetime
    payment_deadline: date

    model_config = ConfigDict(from_attributes=True)


class BookingSummary(BaseModel):
    id: int
    seats: int
    price_per_seat: Decimal
    status: BookingStatus


class BookingUpdate(BaseModel):
    seats_reserved: int = Field(..., ge=1)
