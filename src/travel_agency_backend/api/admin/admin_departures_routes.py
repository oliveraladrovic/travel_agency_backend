import logging
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from ...schemas.departure_schemas import (
    DepartureCreate,
    DepartureOutAdmin,
    DepartureUpdate,
)
from ...db.session import get_session
from ...services import departure_services

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/departures", tags=["admin departures"])


@router.post("/", response_model=DepartureOutAdmin, status_code=status.HTTP_201_CREATED)
def create_departure(
    departure: DepartureCreate, session: Session = Depends(get_session)
):
    logger.info("Attempting to create departure")
    return departure_services.create_departure(session, departure)


@router.get("/", response_model=list[DepartureOutAdmin])
def list_departures(session: Session = Depends(get_session)):
    logger.info("Listing departures for admin")
    return departure_services.list_departures_admin(session)


@router.get("/{departure_id}", response_model=DepartureOutAdmin)
def get_departure(departure_id: int, session: Session = Depends(get_session)):
    logger.info("Get departure %s for admin", departure_id)
    return departure_services.get_departure_admin(session, departure_id)


@router.patch("/{departure_id}", response_model=DepartureOutAdmin)
def update_departure(
    departure_id: int,
    departure_in: DepartureUpdate,
    session: Session = Depends(get_session),
):
    logger.info("Attempting to update departure %s", departure_id)
    return departure_services.update_departure(session, departure_id, departure_in)


@router.delete("/{departure_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_departure(departure_id: int, session: Session = Depends(get_session)):
    logger.info("Attempting to delete departure %s", departure_id)
    return departure_services.delete_departure(session, departure_id)
