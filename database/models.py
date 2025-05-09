# database/models.py
from sqlalchemy import Column, Integer, Text, Numeric, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()

class Consumption(Base):
    __tablename__ = 'consumption'
    id = Column(Integer, primary_key=True, index=True)
    region_code = Column(Integer, index=True, nullable=False)
    region = Column(Text, index=True, nullable=False)
    period = Column(Integer, index=True, nullable=False)
    value = Column(Numeric, nullable=False)

class Region(Base):
    __tablename__ = 'regions'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, index=True, nullable=False)
    geom = Column(Text, nullable=False)

class User(Base):
    __tablename__ = 'users'

    id            = Column(Integer, primary_key=True, index=True)
    email         = Column(Text, unique=True, index=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role          = Column(Text, nullable=False, default='user')
    created_at    = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
