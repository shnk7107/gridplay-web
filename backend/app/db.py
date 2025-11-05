# backend/app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

HERE = os.path.dirname(__file__)
DB_PATH = os.path.join(HERE, "data", "battles.sqlite")
DB_URI = f"sqlite:///{DB_PATH}"

# Create directory if missing
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Engine & session (sync)
engine = create_engine(DB_URI, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    # Import models here to ensure they are registered on Base.metadata
    from . import models_db  # local import to avoid circular imports
    Base.metadata.create_all(bind=engine)
