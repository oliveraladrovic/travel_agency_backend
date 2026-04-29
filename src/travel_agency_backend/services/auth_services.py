from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from ..schemas.user_schemas import UserRegister
from ..models.user_model import User
from ..utils.exceptions import EmailAlreadyExistsError
from ..utils.security import hash_password

logger = logging.getLogger(__name__)


def register_user(session: Session, user_data: UserRegister) -> User:
    existing = session.execute(
        select(User).where(User.email == user_data.email)
    ).scalar_one_or_none()
    if existing:
        logger.warning("User %s already uses same email", existing.id)
        raise EmailAlreadyExistsError()

    new_user = User(
        email=user_data.email, hashed_password=hash_password(user_data.password)
    )
    try:
        session.add(new_user)
        session.commit()
    except IntegrityError:
        session.rollback()
        logger.warning("Integrity error while registering user")
        raise EmailAlreadyExistsError()

    session.refresh(new_user)
    logger.info("User registered with ID: %s", new_user.id)
    return new_user
