# database/user_crud.py
from sqlalchemy import select
from database.db import SessionLocal
from database.models import User
from sqlalchemy.exc import IntegrityError

def get_user_by_email(email: str) -> User | None:
    """
    Возвращает объект User или None, если пользователь не найден.
    """
    with SessionLocal() as db:
        stmt = select(User).where(User.email == email)
        result = db.execute(stmt)
        # scalar_one_or_none сразу отдаёт либо объект, либо None
        return result.scalar_one_or_none()


def create_user(email: str, password_hash: str, is_admin: bool = False) -> User:
    with SessionLocal() as db:
        u = User(
            email=email,
            password_hash=password_hash,
            role='admin' if is_admin else 'user'
        )
        db.add(u)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError(f"User with email {email} already exists")
        db.refresh(u)
        return u
