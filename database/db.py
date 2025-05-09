import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or (
  f"postgresql+psycopg2://"
  f"{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@"
  f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
  f"{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
