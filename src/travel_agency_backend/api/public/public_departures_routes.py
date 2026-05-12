import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...schemas.departure_schemas import DepartureOutPublic
from ...db.session import get_session
from ...services import departure_services

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/departures", tags=["Public routes"])


@router.get("/{departure_id}", response_model=DepartureOutPublic)
def get_departure(departure_id: int, session: Session = Depends(get_session)):
    logger.info("Attempting to show departure %s", departure_id)
    return departure_services.get_departure(session, departure_id)
