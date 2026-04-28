from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..schemas.user_schemas import UserRegister
from ..models.user_model import User
from ..utils.exceptions import EmailAlreadyExistsError
from ..utils.security import hash_password


def register_user(session: Session, user_data: UserRegister) -> User:
    existing = session.execute(
        select(User).where(User.email == user_data.email)
    ).scalar_one_or_none()
    if existing:
        raise EmailAlreadyExistsError()

    new_user = User(
        email=user_data.email, hashed_password=hash_password(user_data.password)
    )
    try:
        session.add(new_user)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise EmailAlreadyExistsError()

    session.refresh(new_user)
    return new_user
