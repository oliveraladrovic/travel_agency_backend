from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
import logging

from ...schemas.trip_schemas import TripOutAdmin, TripCreate
from ...db.session import get_session
from ...services import trip_services

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trips", tags=["admin trips"])


@router.post("/", response_model=TripOutAdmin, status_code=status.HTTP_201_CREATED)
def create_trip(trip: TripCreate, session: Session = Depends(get_session)):
    logger.info("Attempting to create trip")
    return trip_services.create_trip(session, trip)
