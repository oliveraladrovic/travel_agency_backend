from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from slugify import slugify
import logging

from ..models.trip_model import Trip
from ..schemas.trip_schemas import TripCreate
from ..utils.exceptions import TripAlreadyExistsError

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
