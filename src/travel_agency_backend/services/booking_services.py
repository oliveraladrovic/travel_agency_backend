import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date, timedelta, datetime, timezone

from ..models.user_model import User
from ..models.booking_model import Booking
from ..models.departure_model import Departure
from ..models.trip_model import Trip
from ..schemas.booking_schemas import BookingCreate, BookingSummary, BookingUpdate
from ..schemas.departure_schemas import DepartureSummary
from ..utils.enums import BookingStatus
from ..utils.exceptions import (
    UnavailableDepartureError,
    CapacityExceededError,
    BookingNotFoundError,
    InvalidBookingStatusError,
    PaymentDeadlinePassedError,
    BookingUpdateConflictError,
    InvalidNumberOfSeatsError,
)

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


def list_bookings(session: Session, user: User) -> list[Booking]:
    return session.scalars(select(Booking).where(Booking.user_id == user.id)).all()


def list_summary(session: Session, user: User) -> list[DepartureSummary]:
    departures = session.scalars(
        select(Departure).join(Booking).where(Booking.user_id == user.id).distinct()
    ).all()
    return [
        DepartureSummary(
            departure_id=dep.id,
            trip_name=dep.trip.name,
            start_date=dep.start_date,
            total_seats=sum(
                booking.seats_reserved
                for booking in dep.bookings
                if booking.user_id == user.id
            ),
            confirmed_seats=sum(
                booking.seats_reserved
                for booking in dep.bookings
                if booking.status == BookingStatus.CONFIRMED
                and booking.user_id == user.id
            ),
            reserved_seats=sum(
                booking.seats_reserved
                for booking in dep.bookings
                if booking.status == BookingStatus.RESERVED
                and booking.user_id == user.id
            ),
            total_price=sum(
                booking.total_price_snapshot
                for booking in dep.bookings
                if booking.user_id == user.id
            ),
            bookings=[
                BookingSummary(
                    id=booking.id,
                    seats=booking.seats_reserved,
                    price_per_seat=booking.price_per_seat_snapshot,
                    status=booking.status,
                )
                for booking in dep.bookings
                if booking.user_id == user.id
            ],
        )
        for dep in departures
    ]


def get_booking(session: Session, user: User, booking_id: int) -> Booking:
    return _get_booking_or_404(session, user.id, booking_id)


def confirm_booking(session: Session, user: User, booking_id: int) -> Booking:
    booking = _get_booking_or_404(session, user.id, booking_id)
    if booking.status != BookingStatus.RESERVED:
        logger.warning("Booking %s is not in RESERVED status", booking_id)
        raise InvalidBookingStatusError()

    if booking.payment_deadline < date.today():
        logger.warning("Payment deadline for booking %s has passed", booking_id)
        raise PaymentDeadlinePassedError()

    try:
        booking.status = BookingStatus.CONFIRMED
        booking.confirmed_at = datetime.now(timezone.utc)
        session.commit()
    except IntegrityError:
        logger.warning("Integrity error while confirming booking %s", booking_id)
        session.rollback()
        raise BookingUpdateConflictError()

    logger.info("Booking %s confirmed", booking_id)
    session.refresh(booking)
    return booking


def cancel_booking(session: Session, user: User, booking_id: int) -> Booking:
    booking = _get_booking_or_404(session, user.id, booking_id)
    if booking.status != BookingStatus.RESERVED:
        logger.warning("Booking %s is not in RESERVED status", booking_id)
        raise InvalidBookingStatusError()

    try:
        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = datetime.now(timezone.utc)
        session.commit()
    except IntegrityError:
        logger.warning("Integrity error while cancelling booking %s", booking_id)
        session.rollback()
        raise BookingUpdateConflictError()

    logger.info("Booking %s cancelled", booking_id)
    session.refresh(booking)
    return booking


def update_booking(
    session: Session, user: User, update_data: BookingUpdate, booking_id: int
):
    booking = _get_booking_or_404(session, user.id, booking_id)
    if booking.status != BookingStatus.RESERVED:
        logger.warning("Booking %s is not in RESERVED status", booking_id)
        raise InvalidBookingStatusError()

    if update_data.seats_reserved >= booking.seats_reserved:
        logger.warning("Invalid number of seats for update booking %s", booking_id)
        raise InvalidNumberOfSeatsError()

    try:
        booking.seats_reserved = update_data.seats_reserved
        booking.total_price_snapshot = (
            booking.price_per_seat_snapshot * update_data.seats_reserved
        )
        session.commit()
    except IntegrityError:
        logger.warning("Integrity error while cancelling booking %s", booking_id)
        session.rollback()
        raise BookingUpdateConflictError()

    logger.info("Booking %s updated", booking_id)
    session.refresh(booking)
    return booking


def _get_booking_or_404(session: Session, user_id: int, booking_id: int) -> Booking:
    booking = session.scalar(
        select(Booking).where(Booking.id == booking_id, Booking.user_id == user_id)
    )
    if booking is None:
        logger.warning("Booking %s is not available for user %d", booking_id, user_id)
        raise BookingNotFoundError()

    return booking


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


def expire_due_bookings(session: Session):
    logger.info("Starting to expire due bookings")
    to_change = session.scalars(
        select(Booking).where(
            Booking.status == BookingStatus.RESERVED,
            Booking.payment_deadline < date.today(),
        )
    ).all()
    try:
        for booking in to_change:
            booking.status = BookingStatus.EXPIRED
            booking.expired_at = datetime.now(timezone.utc)
        session.commit()
        logger.info("%s due bookings expired", len(to_change))
    except IntegrityError:
        logger.warning("APScheduler failed to expire due bookings")
        session.rollback()
        raise BookingUpdateConflictError()
