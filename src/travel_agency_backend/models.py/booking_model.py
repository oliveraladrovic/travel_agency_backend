from sqlalchemy import (
    Integer,
    ForeignKey,
    Numeric,
    Enum,
    DateTime,
    Date,
    func,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_model import User
    from .departure_model import Departure

from .base import Base
from ..utils.enums import BookingStatus


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint(
            "seats_reserved >= 1 AND seats_reserved <= 10", name="seats_reserved_range"
        ),
        CheckConstraint(
            "price_per_seat_snapshot >= 0", name="price_per_seat_snapshot_non_negative"
        ),
        CheckConstraint(
            "price_per_seat_snapshot >= 0", name="price_per_seat_snapshot_non_negative"
        ),
        CheckConstraint(
            "total_price_snapshot >= 0", name="total_price_snapshot_non_negative"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", name="fk_booking_user"),
        nullable=False,
        index=True,
    )
    departure_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("departures.id", name="fk_booking_departure"),
        nullable=False,
        index=True,
    )
    seats_reserved: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_seat_snapshot: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    total_price_snapshot: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, name="booking_status"),
        default=BookingStatus.RESERVED,
        nullable=False,
        index=True,
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
    payment_deadline: Mapped[date] = mapped_column(Date, nullable=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expired_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    user: Mapped["User"] = relationship("User", back_populates="bookings")
    departure: Mapped["Departure"] = relationship(
        "Departure", back_populates="bookings"
    )
