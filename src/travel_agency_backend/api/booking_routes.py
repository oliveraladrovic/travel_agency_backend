import logging
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from ..schemas.booking_schemas import BookingCreate, BookingOut
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
