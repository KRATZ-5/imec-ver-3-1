# app/services/consumption_service.py
import json
import io
import pandas as pd
from shapely.geometry import shape, mapping
from shapely.ops import unary_union, transform
from pathlib import Path
from fastapi import UploadFile
from app.core.config import DATA_DIR
from database.crud import (
    get_consumption_for_year,
    get_consumption_code_value,
    get_all_regions,
    get_consumption_history,
    create_consumption_record
)
from database.db import SessionLocal
from database.models import Consumption

# --- Helper functions ---

def wrap_longitude(x, y, z=None):
    """
    Если долгота > 180, переносим значение в отрицательный диапазон
    для корректного отображения на карте.
    """
    if x > 180:
        x -= 360
    elif x < -100:
        x += 360
    return (x, y)

# --- Regions loading ---

def load_regions() -> dict:
    """
    Получает список регионов из БД и формирует GeoJSON FeatureCollection:
      properties.code = ID региона
      properties.name = Название региона
    """
    regions = get_all_regions()
    features = []
    for r in regions:
        features.append({
            "type": "Feature",
            "geometry": r["geometry"],
            "properties": {"code": r["id"], "name": r["name"]}
        })
    return {"type": "FeatureCollection", "features": features}

# --- Consumption loading ---

def load_consumption(period: int=None) -> list[dict]:
    """
    Возвращает список словарей {region_code, value} за указанный год.
    Если period не указан, бросает ValueError.
    """
    if period is None:
        raise ValueError("period must be specified")
    return get_consumption_for_year(period)

# --- Consumption history ---

def load_consumption_history(region_code: int) -> list[dict]:
    return get_consumption_history(region_code)

# --- Aggregations ---

def aggregate_by_region(period: int) -> pd.DataFrame:
    """
    Возвращает DataFrame с колонками region_code и value за указанный год.
    """
    data = get_consumption_code_value(period)
    return pd.DataFrame(data, columns=["region_code", "value"])

# --- CSV import and management ---

async def import_consumption_csv(csv_file: UploadFile) -> int:
    """
    Импортирует новые данные из CSV-файла и заменяет старые
    данные только для годов, присутствующих в файле.
    Возвращает количество импортированных записей.
    """

    # 1. Читаем всё тело файла в память и создаём текстовый буфер
    try:
       raw = await csv_file.read()
       text = raw.decode('utf-8-sig')  # убираем BOM, если есть
       buffer = io.StringIO(text)
       df = pd.read_csv(
           buffer,
           dtype = {'region_code': int, 'region': str, 'period': int, 'value': float}
        )
    except Exception as e:
        raise ValueError(f"Error reading CSV: {e}")

    # 2. Валидация
    required_cols = {'region_code', 'region', 'period', 'value'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required_cols}")
    df = df.dropna(subset=['region_code', 'period', 'value'])
    df['region_code'] = df['region_code'].astype(int)
    df['period'] = df['period'].astype(int)
    df['value'] = df['value'].astype(float)

    # 3. Список годов для замены
    periods = df['period'].unique().tolist()

    session = SessionLocal()
    try:
        # 4. Удалить старые данные только для этих годов
        session.query(Consumption) \
               .filter(Consumption.period.in_(periods)) \
               .delete(synchronize_session=False)
        session.commit()
        # 5. Массовая вставка
        records = df.to_dict(orient='records')
        session.bulk_insert_mappings(Consumption, records)
        session.commit()
        return len(records)

    except Exception as e:
        session.rollback()
        raise ValueError(f"Error importing data: {e}")
    finally:
        session.close()

async def delete_consumption(periods: list[int] = None, region_code: int = None) -> int:
    """
    Удаляет записи потребления по заданным годам и/или region_code.
    Возвращает число удалённых записей.
    Если не указаны ни periods, ни region_code, удаляет всё.
    """
    session = SessionLocal()
    try:
        query = session.query(Consumption)
        if periods:
            query = query.filter(Consumption.period.in_(periods))
        if region_code is not None:
            query = query.filter(Consumption.region_code == region_code)
        deleted = query.delete(synchronize_session=False)
        session.commit()
        return deleted
    except Exception as e:
        session.rollback()
        raise ValueError(f"Error deleting consumption: {e}")
    finally:
        session.close()


async def manual_add_consumption(region_code: int, period: int, value: float) -> dict:
    """
    Вставляет одну запись потребления, возвращает вставленные данные.
    """
    rec = create_consumption_record(region_code, period, value)
    return {
        "region_code": rec.region_code,
        "region": rec.region,
        "period": rec.period,
        "value": float(rec.value)
    }

if __name__ == "__main__":
    # Генерация файла all_regions.geojson для отладки
    fc = load_regions()
    out_path = Path.cwd() / "all_regions.geojson"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, indent=2)
    print(f"Generated GeoJSON with {len(fc['features'])} features to {out_path}")
