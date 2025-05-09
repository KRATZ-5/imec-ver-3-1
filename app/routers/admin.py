from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Request, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.consumption_service import import_consumption_csv, delete_consumption
from app.dependencies import get_current_user, admin_required

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse, summary="Админская панель")
async def admin_get(request: Request, user=Depends(admin_required)):
    # Если пользователь прошёл admin_required, значит он админ
    return templates.TemplateResponse("admin.html", {"request": request, "user": user})

@router.post(
    "/consumption/import",
    summary="Импорт CSV в БД",
    response_class=JSONResponse
)
async def admin_import_consumption(
    csv_file: UploadFile = File(...),
    user=Depends(admin_required)
):
    try:
        count = await import_consumption_csv(csv_file)
        return JSONResponse({"imported": count})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete(
    "/consumption",
    summary="Удалить данные потребления",
    response_class=JSONResponse
)
async def admin_delete_consumption(
    periods: list[int] | None = Body(
        None,
        description="Список годов для удаления"
    ),
    region_code: int | None = Body(
        None,
        description="Код региона для удаления"
    ),
    user=Depends(admin_required)
):
    try:
        deleted = await delete_consumption(periods, region_code)
        return JSONResponse({"deleted": deleted})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
