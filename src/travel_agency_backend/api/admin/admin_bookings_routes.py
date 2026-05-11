import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...schemas.booking_schemas import BookingOutAdmin
from ...db.session import get_session
from ...services import booking_services

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bookings", tags=["Admin: Bookings"])


@router.get("/", response_model=list[BookingOutAdmin])
def list_bookings(session: Session = Depends(get_session)):
    logger.info("Attempting to list bookings for admin")
    return booking_services.list_bookings_admin(session)


@router.get("/{booking_id}", response_model=BookingOutAdmin)
def get_booking(booking_id: int, session: Session = Depends(get_session)):
    logger.info("Attempting to get booking %s", booking_id)
    return booking_services.get_booking_admin(session, booking_id)
