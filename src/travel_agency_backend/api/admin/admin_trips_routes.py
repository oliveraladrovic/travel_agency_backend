from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
import logging

from ...schemas.trip_schemas import TripOutAdmin, TripCreate, TripUpdate
from ...db.session import get_session
from ...services import trip_services

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trips", tags=["admin trips"])


@router.post("/", response_model=TripOutAdmin, status_code=status.HTTP_201_CREATED)
def create_trip(trip: TripCreate, session: Session = Depends(get_session)):
    logger.info("Attempting to create trip")
    return trip_services.create_trip(session, trip)


@router.get("/", response_model=list[TripOutAdmin])
def list_trips(session: Session = Depends(get_session)):
    logger.info("Listing trips for admin")
    return trip_services.list_trips_admin(session)


@router.get("/{trip_id}", response_model=TripOutAdmin)
def get_trip(trip_id: int, session: Session = Depends(get_session)):
    logger.info("Get trip %s for admin", trip_id)
    return trip_services.get_trip_admin(session, trip_id)


@router.patch("/{trip_id}", response_model=TripOutAdmin)
def update_trip(
    trip_id: int, trip_in: TripUpdate, session: Session = Depends(get_session)
):
    logger.info("Attempting to update trip %s", trip_id)
    return trip_services.update_trip(session, trip_id, trip_in)


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: int, session: Session = Depends(get_session)):
    logger.info("Attempting to delete trip %s", trip_id)
    return trip_services.delete_trip(session, trip_id)
