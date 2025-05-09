import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy import text
from database.db import engine
from database.models import Base

with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    conn.commit()

Base.metadata.create_all(bind=engine)

load_dotenv()

# Собираем URL (или читаем из окружения)
DATABASE_URL = os.getenv("DATABASE_URL") or (
    f"postgresql+psycopg2://"
    f"{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

# Диагностика: напечатаем то, что реально в переменной
print("→ [DEBUG] DATABASE_URL =", DATABASE_URL)

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
