# database/crud.py
import json
from sqlalchemy import select, func
from database.db import SessionLocal
from database.models import Consumption, Region
from database.models import User
from sqlalchemy.exc import NoResultFound

# def get_user_by_username(username: str) -> User | None:
#     with SessionLocal() as db:
#         return db.query(User).filter(User.username == username).first()

def create_consumption_record(region_code: int, period: int, value: float) -> Consumption:
    """
    Вставляет новую запись о потреблении в БД.
    """
    with SessionLocal() as session:
        # находим название региона
        try:
            region = session.execute(
                select(Region.name).where(Region.id == region_code)
            ).scalar_one()
        except NoResultFound:
            raise ValueError(f"Region with code {region_code} not found")

        rec = Consumption(
            region_code=region_code,
            region=region,
            period=period,
            value=value
        )
        session.add(rec)
        session.commit()
        session.refresh(rec)
        return rec



def get_consumption_for_year(period: int):
    """
    Возвращает список словарей с полями 'region_code' и 'value' для заданного года.
    """
    with SessionLocal() as session:
        stmt = (
            select(
                Consumption.region_code.label("region_code"),
                func.sum(Consumption.value).label("value")
            )
            .where(Consumption.period == period)
            .group_by(Consumption.region_code)
        )
        rows = session.execute(stmt).all()
        return [{"region_code": r.region_code, "value": float(r.value)} for r in rows]

def get_all_regions():
    """
    Возвращает список регионов из БД со структурами:
    {
      "id": <region_id>,
      "name": <region_name>,
      "geometry": <GeoJSON geometry>
    }
    """
    with SessionLocal() as session:
        stmt = select(
            Region.id.label("id"),
            Region.name.label("name"),
            Region.geom.label("geom_json")     # теперь просто текст
        )
        rows = session.execute(stmt).all()
        features = []
        for r in rows:
            # geom_json уже строка с JSON — парсим её
            geom = json.loads(r.geom_json)
            features.append({
                "id":   r.id,
                "name": r.name,
                "geometry": geom
            })
        return features

def get_consumption_code_value(year: int) -> list[tuple[int, float]]:
    with SessionLocal() as session:
        stmt = (
            select(Consumption.region_code, func.sum(Consumption.value))
            .where(Consumption.period == year)
            .group_by(Consumption.region_code)
        )
        return session.execute(stmt).all()

def get_consumption_history(region_code: int) -> list[dict]:
    """
    Возвращает список словарей {'period': int, 'value': float}
    со всеми годами для заданного региона.
    """
    with SessionLocal() as session:
        stmt = (
            select(
                Consumption.period.label("period"),
                Consumption.value.label("value")
            )
            .where(Consumption.region_code == region_code)
            .order_by(Consumption.period)
        )
        rows = session.execute(stmt).all()
        return [
            {"period": r.period, "value": float(r.value)}
            for r in rows
        ]

def get_period_range() -> tuple[int, int]:
    """
    Возвращает (min_period, max_period) из таблицы consumption.
    """
    with SessionLocal() as session:
        min_year, max_year = session.query(
            func.min(Consumption.period),
            func.max(Consumption.period)
        ).one()
        # Приводим к int на случай, если пустая БД вернёт Decimal/None
        return int(min_year or 0), int(max_year or 0)