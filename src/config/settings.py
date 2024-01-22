import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
WAREHOUSE_DIR = DATA_DIR / "warehouse"

BCRP_BASE_URL = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
BCRP_DEFAULT_START = "2010-1"
BCRP_DEFAULT_END = "2023-12"

BCRP_REQUEST_TIMEOUT = 30
BCRP_MAX_RETRIES = 3
BCRP_RETRY_BACKOFF = 2.0
BCRP_RATE_LIMIT_SECONDS = 1.5

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "bcrp_warehouse")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
