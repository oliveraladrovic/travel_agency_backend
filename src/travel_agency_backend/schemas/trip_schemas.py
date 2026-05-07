from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class TripCreate(BaseModel):
    name: str
    description: str | None = None
    duration_days: int = Field(..., ge=1)
    is_active: bool = False


class TripUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    duration_days: int | None = Field(default=None, ge=1)
    is_active: bool | None = None


class TripOutAdmin(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None = None
    duration_days: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TripOutUnprotected(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None = None
    duration_days: int

    model_config = ConfigDict(from_attributes=True)
