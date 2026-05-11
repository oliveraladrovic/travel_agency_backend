import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..schemas.user_schemas import UserNewRole, UserNewStatus
from ..models.user_model import User
from ..models.booking_model import Booking
from ..utils.exceptions import (
    UserNotFoundError,
    UserUpdateConflictError,
    ActiveBookingExistsError,
)
from ..utils.enums import BookingStatus

logger = logging.getLogger(__name__)


def list_users(session: Session) -> list[User]:
    return session.scalars(select(User)).all()


def update_user_role(session: Session, user_id: int, new_role: UserNewRole) -> User:
    user = _get_user_or_404(session, user_id)

    try:
        user.role = new_role.role
        session.commit()
    except IntegrityError:
        session.rollback()
        logger.warning("Integrity error while updating role for user %s", user_id)
        raise UserUpdateConflictError()

    logger.info("User %d updated to %s", user_id, new_role.role.value)
    return user


def update_user_status(
    session: Session, user_id: int, new_status: UserNewStatus
) -> User:
    user = _get_user_or_404(session, user_id)

    if new_status.is_active == user.is_active:
        logger.info("New status for user %s is same as old status", user_id)
        return user

    if new_status.is_active is False:
        active_bookings = session.scalar(
            select(Booking).where(
                Booking.user_id == user_id,
                Booking.status.in_([BookingStatus.RESERVED, BookingStatus.CONFIRMED]),
            )
        )
        if active_bookings:
            logger.warning("Cannot deactivate user with active bookings")
            raise ActiveBookingExistsError()

        user.is_active = False

    if new_status.is_active is True:
        user.is_active = True

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        logger.warning("Integrity error while updating status for user %s", user_id)
        raise UserUpdateConflictError()

    logger.info("Status for user %s updated", user_id)
    return user


def _get_user_or_404(session: Session, user_id: int) -> User:
    user = session.scalar(select(User).where(User.id == user_id))
    if user is None:
        logger.warning("User %s not found", user_id)
        raise UserNotFoundError()

    return user
