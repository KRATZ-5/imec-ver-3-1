import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.core.config import BASE_DIR
from app.core.config import STATIC_DIR
from app.routers import views, auth, api_regions, api_consumption, admin
from fastapi.exception_handlers import http_exception_handler as default_http_handler
import urllib.parse
from app.routers import admin
from database.db import engine
from database.models import Base
from sqlalchemy import text

Base.metadata.create_all(bind=engine)
app = FastAPI()

# # Включаем PostGIS, если ещё не включено
# with engine.connect() as conn:
#     conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
#     conn.commit()

Base.metadata.create_all(bind=engine)
app.include_router(admin.router)
static_path = os.path.join(BASE_DIR, "app", "static")

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)
@app.exception_handler(HTTPException)
async def auth_exception_handler(request: Request, exc: HTTPException):
    # Если это наша 401 — редиректим на /login
    if exc.status_code == 401:
        text = urllib.parse.quote("Для доступа к карте нужно войти в систему")
        return RedirectResponse(url=f"/login?msg={text}")
    # Для остальных HTTPException используем стандартный обработчик
    return await default_http_handler(request, exc)
app.include_router(views.router)
app.include_router(auth.router)
app.include_router(api_regions.router)
app.include_router(api_consumption.router)
app.include_router(admin.router)
