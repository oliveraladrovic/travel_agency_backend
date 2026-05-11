import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...schemas.user_schemas import UserOutAdmin, UserNewRole, UserNewStatus
from ...db.session import get_session
from ...services import user_services

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Admin: Users"])


@router.post("/{user_id}/role", response_model=UserOutAdmin)
def update_user_role(
    user_id: int, user_role: UserNewRole, session: Session = Depends(get_session)
):
    logger.info("Attempting to update role for user %s", user_id)
    return user_services.update_user_role(session, user_id, user_role)


@router.post("/{user_id}/status", response_model=UserOutAdmin)
def update_user_status(
    user_id: int, user_status: UserNewStatus, session: Session = Depends(get_session)
):
    logger.info("Attempting to update status for user %s", user_id)
    return user_services.update_user_status(session, user_id, user_status)


@router.get("/", response_model=list[UserOutAdmin])
def list_users(session: Session = Depends(get_session)):
    logger.info("Attempting to list users for admin")
    return user_services.list_users(session)
