from database.user_crud import get_user_by_email, create_user
from app.core.security import hash_password, verify_password
from database.models import User

def register_user(email: str, raw_password: str, is_admin: bool = False) -> User:
    if get_user_by_email(email):
        raise ValueError("User already exists")
    hashed = hash_password(raw_password)
    return create_user(email=email, password_hash=hashed, is_admin=is_admin)

def authenticate_user(email: str, raw_password: str) -> User | None:
    user = get_user_by_email(email)
    if not user or not verify_password(raw_password, user.password_hash):
        return None
    return user
