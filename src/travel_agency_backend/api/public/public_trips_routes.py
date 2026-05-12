import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...schemas.trip_schemas import TripOutPublic
from ...schemas.departure_schemas import DepartureOutPublic
from ...db.session import get_session
from ...services import trip_services, departure_services

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trips", tags=["Public routes"])


@router.get("/", response_model=list[TripOutPublic])
def list_trips(session: Session = Depends(get_session)):
    logger.info("Attempting to list public trips")
    return trip_services.list_trips(session)


@router.get("/{trip_id}", response_model=TripOutPublic)
def get_trip(trip_id: int, session: Session = Depends(get_session)):
    logger.info("Attempting to show trip %s", trip_id)
    return trip_services.get_trip(session, trip_id)


@router.get("/{trip_id}/departures", response_model=list[DepartureOutPublic])
def list_departures_for_trip(trip_id: int, session: Session = Depends(get_session)):
    logger.info("Attempting to list public departures for trip %s", trip_id)
    return departure_services.list_departures_by_trip(session, trip_id)
