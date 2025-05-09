# app/dependencies.py

from fastapi import Depends, HTTPException, status, Cookie
from app.core.security import decode_token
from database.user_crud import get_user_by_email

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
)

async def get_current_user(token: str = Cookie(None)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        data = decode_token(token)
        email = data.get("sub")
        role  = data.get("role", "user")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    user.role = role
    return user

def admin_required(current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user
