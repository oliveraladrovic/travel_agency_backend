from sqlalchemy import (
    Integer,
    ForeignKey,
    Numeric,
    Boolean,
    Date,
    DateTime,
    func,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .trip_model import Trip
    from .booking_model import Booking

from .base import Base


class Departure(Base):
    __tablename__ = "departures"
    __table_args__ = (
        CheckConstraint("capacity > 0", name="capacity_positive"),
        CheckConstraint("price_per_seat > 0", name="price_per_seat_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trip_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("trips.id", name="fk_departure_trip"),
        nullable=False,
        index=True,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_seat: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    trip: Mapped["Trip"] = relationship("Trip", back_populates="departures")
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking", back_populates="departure"
    )
