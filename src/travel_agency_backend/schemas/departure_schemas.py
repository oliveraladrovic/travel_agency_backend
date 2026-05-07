from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from decimal import Decimal


class DepartureCreate(BaseModel):
    trip_id: int
    start_date: date
    capacity: int = Field(..., gt=0)
    price_per_seat: Decimal = Field(..., gt=0)
    is_active: bool = False


class DepartureUpdate(BaseModel):
    trip_id: int | None = None
    start_date: date | None = None
    capacity: int | None = Field(default=None, gt=0)
    price_per_seat: Decimal | None = Field(default=None, gt=0)
    is_active: bool | None = None


class DepartureOutAdmin(BaseModel):
    id: int
    trip_id: int
    start_date: date
    capacity: int
    price_per_seat: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DepartureOutUnprotected(BaseModel):
    id: int
    trip_id: int
    start_date: date
    capacity: int
    price_per_seat: Decimal

    model_config = ConfigDict(from_attributes=True)
