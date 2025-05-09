# app/routers/auth.py
from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER
from starlette.templating import Jinja2Templates

from app.services.user_service import register_user, authenticate_user
from app.core.security import create_token

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/login")
async def login_post(
    request: Request,
    email:    str = Form(...),
    password: str = Form(...)
):
    user = authenticate_user(email, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "msg": "Invalid credentials"},
            status_code=400
        )

    # создаём JWT с полями sub (email) и role
    token = create_token({"sub": user.email, "role": user.role})
    resp = RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)
    resp.set_cookie("token", token, httponly=True)
    return resp


@router.post("/register")
async def register_post(
    request:  Request,
    email:    str = Form(...),
    password: str = Form(...)
):
    try:
        user = register_user(email, password, is_admin=False)
    except ValueError as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "msg": str(e)},
            status_code=400
        )

    return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)
