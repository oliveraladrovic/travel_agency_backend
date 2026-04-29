from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging

from ..schemas.user_schemas import UserRegister, UserLogin, UserOutBasic
from ..schemas.token_schema import Token
from ..db.session import get_session
from ..services import auth_services
from ..config.settings import settings
from ..utils.security import get_current_user
from ..models.user_model import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserOutBasic, status_code=status.HTTP_201_CREATED
)
def register_user(user: UserRegister, session: Session = Depends(get_session)):
    logger.info("Attempting to register user")
    return auth_services.register_user(session, user)


@router.post("/login", response_model=Token)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    logger.info("Attempting to login user")
    user = UserLogin(email=form_data.username, password=form_data.password)
    access_token = auth_services.login_user(session, user)
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserOutBasic)
def get_current_user_info(user: User = Depends(get_current_user)):
    logger.info("Fetching current user info")
    return user
