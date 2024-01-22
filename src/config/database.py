from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from src.config.settings import DATABASE_URL


def create_db_engine() -> Engine:
    return create_engine(DATABASE_URL, pool_pre_ping=True)
