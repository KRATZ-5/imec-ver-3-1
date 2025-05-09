import jwt
from passlib.hash import bcrypt
from .config import SECRET_KEY

def create_token(data: dict) -> str:
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(password: str, hash_: str) -> bool:
    return bcrypt.verify(password, hash_)
