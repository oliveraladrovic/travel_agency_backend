from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config.settings import settings
from ..utils.exceptions import (
    InvalidTokenError,
    TokenExpiredError,
    AdminPrivilegesRequiredError,
)
from ..db.session import get_session
from ..models.user_model import User
from ..utils.enums import UserRole

hasher = PasswordHasher()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def hash_password(password: str) -> str:
    return hasher.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        hasher.verify(hashed_password, password)
        return True
    except VerifyMismatchError:
        return False


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except jwt.InvalidTokenError:
        raise InvalidTokenError()

    user_id_raw = payload.get("sub")
    try:
        user_id = int(user_id_raw)
    except (ValueError, TypeError):
        raise InvalidTokenError()

    user = session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise InvalidTokenError()

    if not user.is_active:
        raise InvalidTokenError()

    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise AdminPrivilegesRequiredError()
    return user
