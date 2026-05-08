import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date, timedelta

from ..models.user_model import User
from ..models.booking_model import Booking
from ..models.departure_model import Departure
from ..models.trip_model import Trip
from ..schemas.booking_schemas import BookingCreate
from ..utils.enums import BookingStatus
from ..utils.exceptions import UnavailableDepartureError, CapacityExceededError

logger = logging.getLogger(__name__)


def create_booking(
    session: Session, user: User, booking_data: BookingCreate
) -> Booking:
    departure = _get_valid_departure_or_404(session, booking_data.departure_id)
    _validate_seats_available(departure, booking_data.seats_reserved, user.id)
    total_price = booking_data.seats_reserved * departure.price_per_seat
    new_booking = Booking(
        user_id=user.id,
        departure_id=departure.id,
        seats_reserved=booking_data.seats_reserved,
        price_per_seat_snapshot=departure.price_per_seat,
        total_price_snapshot=total_price,
        status=BookingStatus.RESERVED,
        payment_deadline=max(date.today(), departure.start_date - timedelta(days=15)),
    )
    try:
        session.add(new_booking)
        session.commit()
    except IntegrityError:
        session.rollback()
        logger.warning("Integrity error while creating booking for user %s", user.id)
        raise UnavailableDepartureError()

    session.refresh(new_booking)
    logger.info("Booking %s created for user %d", new_booking.id, user.id)
    return new_booking


def _get_valid_departure_or_404(session: Session, departure_id: int) -> Departure:
    departure = session.scalar(
        select(Departure)
        .join(Trip)
        .where(
            Departure.id == departure_id,
            Departure.is_active,
            Departure.start_date > date.today(),
            Trip.is_active,
        )
    )
    if departure is None:
        logger.warning("Departure %s is not available for booking", departure_id)
        raise UnavailableDepartureError()

    return departure


def _validate_seats_available(
    departure: Departure, number_of_seats: int, user_id: int
) -> None:
    reserved = 0
    user_seats = 0
    for booking in departure.bookings:
        if booking.status in (BookingStatus.RESERVED, BookingStatus.CONFIRMED):
            reserved += booking.seats_reserved
            if booking.user_id == user_id:
                user_seats += booking.seats_reserved

    if (
        reserved + number_of_seats > departure.capacity
        or user_seats + number_of_seats > 10
    ):
        logger.info("Not enough available seats for user %s", user_id)
        raise CapacityExceededError()
