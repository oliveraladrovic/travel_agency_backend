from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..schemas.user_schemas import UserRegister, UserOutBasic
from ..db.session import get_session
from ..services import auth_services

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserOutBasic, status_code=status.HTTP_201_CREATED
)
def register_user(user: UserRegister, session: Session = Depends(get_session)):
    return auth_services.register_user(session, user)
