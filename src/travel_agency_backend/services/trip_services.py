from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from slugify import slugify
import logging

from ..models.trip_model import Trip
from ..schemas.trip_schemas import TripCreate, TripUpdate
from ..utils.exceptions import (
    TripAlreadyExistsError,
    TripNotFoundError,
    DeleteConflictError,
)

logger = logging.getLogger(__name__)


def create_trip(session: Session, trip_data: TripCreate) -> Trip:
    slug = slugify(trip_data.name)
    existing = session.execute(
        select(Trip).where(Trip.slug == slug)
    ).scalar_one_or_none()
    if existing:
        logger.warning("Trip slug already exists")
        raise TripAlreadyExistsError()

    new_trip = Trip(
        name=trip_data.name,
        slug=slug,
        description=trip_data.description,
        duration_days=trip_data.duration_days,
        is_active=trip_data.is_active,
    )
    try:
        session.add(new_trip)
        session.commit()
    except IntegrityError:
        session.rollback()
        logger.warning("Integrity error while creating trip")
        raise TripAlreadyExistsError()

    session.refresh(new_trip)
    logger.info("Trip with ID %s created successfully", new_trip.id)
    return new_trip


def list_trips_admin(session: Session) -> list[Trip]:
    return session.scalars(select(Trip)).all()


def get_trip_admin(session: Session, trip_id: int) -> Trip:
    return _get_trip_or_404(session, trip_id)


def update_trip(session: Session, trip_id: int, trip_data: TripUpdate):
    trip = _get_trip_or_404(session, trip_id)

    update_data = trip_data.model_dump(exclude_unset=True)
    if not update_data:
        return trip

    for attr, value in update_data.items():
        if attr == "name":
            new_name = update_data.get("name")
            new_slug = slugify(new_name)
            existing = session.scalar(
                select(Trip).where(Trip.slug == new_slug, Trip.id != trip_id)
            )
            if existing:
                logger.warning("Trip with name %s already exists", new_name)
                raise TripAlreadyExistsError()

            trip.name = new_name
            trip.slug = new_slug
            continue

        setattr(trip, attr, value)

    try:
        session.commit()
        logger.info("Trip updated successfully")
    except IntegrityError:
        session.rollback()
        logger.warning("Integrity error while updating trip %s", trip_id)
        raise TripAlreadyExistsError()

    session.refresh(trip)
    return trip


def delete_trip(session: Session, trip_id: int) -> None:
    trip = _get_trip_or_404(session, trip_id)

    # If departures are linked to trip then only soft delete
    if not trip.departures:
        session.delete(trip)
    else:
        trip.is_active = False

    try:
        session.commit()
        logger.info("Trip %s successfully deleted", trip_id)
    except IntegrityError:
        session.rollback()
        logger.warning("Integrity error while deleting trip %s", trip_id)
        raise DeleteConflictError()
    return


def _get_trip_or_404(session: Session, trip_id: int) -> Trip:
    trip = session.scalar(select(Trip).where(Trip.id == trip_id))
    if trip is None:
        logger.warning("Trip %s not found", trip_id)
        raise TripNotFoundError()

    logger.info("Trip %s fetched", trip.id)
    return trip
