# app/routers/api_consumption.py
from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.dependencies import get_current_user, admin_required
from pydantic import BaseModel, Field
from app.services.consumption_service import (
    load_consumption,
    load_consumption_history,
    manual_add_consumption
)
router = APIRouter(prefix="/api/consumption", tags=["consumption"])

class ConsumptionCreate(BaseModel):
    region_code: int = Field(..., description="Код региона")
    period:      int = Field(..., description="Год")
    value:       float = Field(..., description="Потребление, млн кВт·ч")


@router.get("", response_class=JSONResponse)
async def api_consumption(
    period: int | None = Query(None, description="Год в формате YYYY"),
    user=Depends(get_current_user),
):
    if period is None:
        raise HTTPException(400, "Параметр period обязателен")
    data = load_consumption(period)
    return JSONResponse(content=data)

@router.post(
    "",
    response_class=JSONResponse,
    summary="Добавить запись потребления (только админ)"
)
async def api_consumption_add(
    payload: ConsumptionCreate,
    user=Depends(admin_required)
):
    try:
        rec = await manual_add_consumption(
            payload.region_code, payload.period, payload.value
        )
        return JSONResponse(rec)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/history", response_class=JSONResponse)
async def api_consumption_history(
    region_code: int = Query(..., description="Код региона"),
    user=Depends(get_current_user),
):
    # история по всем годам
    history = load_consumption_history(region_code)
    if not history:
        raise HTTPException(404, f"No data for region {region_code}")
    return JSONResponse(content=history)
