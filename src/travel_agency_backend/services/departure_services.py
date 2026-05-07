from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging
from datetime import date

from ..schemas.departure_schemas import DepartureCreate, DepartureUpdate
from ..models.departure_model import Departure
from .trip_services import _get_trip_or_404
from ..utils.exceptions import (
    DepartureNotFoundError,
    UpdateConflictError,
    DeleteConflictError,
    InvalidDepartureDateError,
    DepartureIntegrityError,
)

logger = logging.getLogger(__name__)


def create_departure(session: Session, departure_data: DepartureCreate) -> Departure:
    _get_trip_or_404(session, departure_data.trip_id)

    if departure_data.start_date <= date.today():
        logger.warning("Departure start_date must be in future")
        raise InvalidDepartureDateError()

    new_departure = Departure(
        trip_id=departure_data.trip_id,
        start_date=departure_data.start_date,
        capacity=departure_data.capacity,
        price_per_seat=departure_data.price_per_seat,
        is_active=departure_data.is_active,
    )

    try:
        session.add(new_departure)
        session.commit()
    except IntegrityError:
        session.rollback()
        logger.warning("Integrity error while creating departure")
        raise DepartureIntegrityError()

    session.refresh(new_departure)
    logger.info("Departure with ID %s created successfully", new_departure.id)
    return new_departure


def list_departures_admin(session: Session) -> list[Departure]:
    return session.scalars(select(Departure)).all()


def get_departure_admin(session: Session, departure_id: int) -> Departure:
    return _get_departure_or_404(session, departure_id)


def update_departure(
    session: Session, departure_id: int, departure_data: DepartureUpdate
) -> Departure:
    departure = _get_departure_or_404(session, departure_id)

    update_data = departure_data.model_dump(exclude_unset=True)
    if not update_data:
        return departure

    for attr, value in update_data.items():
        if attr == "trip_id":
            _get_trip_or_404(session, value)
        if attr == "start_date" and value <= date.today():
            logger.warning("Departure start_date must be in future")
            raise InvalidDepartureDateError()

        setattr(departure, attr, value)

    try:
        session.commit()
        logger.info("Departure %s updated successfully", departure_id)
    except IntegrityError:
        session.rollback()
        logger.warning("Integrity error while updating departure %s", departure_id)
        raise UpdateConflictError()

    session.refresh(departure)
    return departure


def delete_departure(session: Session, departure_id: int) -> None:
    departure = _get_departure_or_404(session, departure_id)

    # If bookings are linked to departure then only soft delete
    if not departure.bookings:
        session.delete(departure)
    else:
        departure.is_active = False

    try:
        session.commit()
        logger.info("Departure %s successfully deleted", departure_id)
    except IntegrityError:
        session.rollback()
        logger.warning("Integrity error while deleting departure %s", departure_id)
        raise DeleteConflictError()
    return


def _get_departure_or_404(session: Session, departure_id: int) -> Departure:
    departure = session.scalar(select(Departure).where(Departure.id == departure_id))
    if departure is None:
        logger.warning("Departure %s not found", departure_id)
        raise DepartureNotFoundError()

    logger.info("Departure %s fetched", departure.id)
    return departure
