from database.db import SessionLocal
from database.models import User

def get_user_by_email(email: str) -> User | None:
    with SessionLocal() as db:
        return db.query(User).filter(User.email == email).first()

def create_user(email: str, password_hash: str, is_admin: bool = False) -> User:
    with SessionLocal() as db:
        u = User(
            email=email,
            password_hash=password_hash,
            role='admin' if is_admin else 'user'
        )
        db.add(u)
        db.commit()
        db.refresh(u)
        return u
