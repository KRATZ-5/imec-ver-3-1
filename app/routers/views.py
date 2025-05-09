from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.dependencies import get_current_user
from database.crud import get_period_range

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
# async def index(request: Request, user=Depends(get_current_user)):
#     # Больше не строю карту на сервере — всё в JS
#     return templates.TemplateResponse("index.html", {
#         "request": request,
#         "user": user
#     })
async def index(request: Request, user=Depends(get_current_user)):
    # Подтягиваем динамический диапазон годов для слайдера
    min_year, max_year = get_period_range()
    return templates.TemplateResponse("index.html", {
        "request":   request,
        "user":      user,
        "min_year":  min_year,
        "max_year":  max_year,
    })
@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request, msg: str | None = Query(None)):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "msg": msg
    })

@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/logout")
async def logout():
    resp = RedirectResponse(url="/login")
    resp.delete_cookie("token")
    return resp
