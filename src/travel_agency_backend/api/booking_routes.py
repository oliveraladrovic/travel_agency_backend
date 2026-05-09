import logging
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from ..schemas.booking_schemas import BookingCreate, BookingOut
from ..schemas.departure_schemas import DepartureSummary
from ..models.user_model import User
from ..utils.security import get_current_user
from ..db.session import get_session
from ..services import booking_services

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking: BookingCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    logger.info("User %s attempting to create booking", user.id)
    return booking_services.create_booking(session, user, booking)


@router.get("/me", response_model=list[BookingOut])
def list_bookings(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    logger.info("Attempting to list bookings for user %s", user.id)
    return booking_services.list_bookings(session, user)


@router.get("/me/summary", response_model=list[DepartureSummary])
def list_summary(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    logger.info("Attempting to get summary for user %s", user.id)
    return booking_services.list_summary(session, user)


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    logger.info("User %s attempting to get booking %d", user.id, booking_id)
    return booking_services.get_booking(session, user, booking_id)
