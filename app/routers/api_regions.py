from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.services.consumption_service import load_regions   # <-- берём из нового модуля
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/api/regions",
    tags=["regions"]
)

@router.get("", response_class=JSONResponse, summary="Вернуть GeoJSON всех регионов")
async def api_regions(user=Depends(get_current_user)):
    """
    Возвращает единый GeoJSON со всеми регионами,
    найденными в папке DATA_DIR/Regions.
    """
    data = load_regions()
    if not data.get("features"):
        raise HTTPException(status_code=404, detail="Regions not found")
    return JSONResponse(content=data)
