import json
from datetime import date, datetime

import pandas as pd

from src.config.series import SERIES_CATALOG, SerieConfig
from src.config.settings import RAW_DIR
from src.extract.bcrp_client import BCRPClient
from src.utils.date_parser import parse_bcrp_period
from src.utils.logger import setup_logger

logger = setup_logger("extract.ingestion")

CONTROL_FILE = RAW_DIR / ".etl_control.json"


class IncrementalIngestion:
    def __init__(self, client: BCRPClient | None = None) -> None:
        self.client = client or BCRPClient()
        self.control = self._load_control()

    def extract_all(self, mode: str = "incremental") -> pd.DataFrame:
        all_records: list[dict] = []

        for codigo, config in SERIES_CATALOG.items():
            records = self._extract_serie(codigo, config, mode)
            all_records.extend(records)
            logger.info(f"{codigo} ({config.nombre}): {len(records)} registros")

        if not all_records:
            logger.warning("No se extrajeron registros nuevos")
            return pd.DataFrame()

        df = pd.DataFrame(all_records)
        logger.info(f"Total extraido: {len(df)} registros de {len(SERIES_CATALOG)} series")
        return df

    def extract_series(self, codigos: list[str], mode: str = "incremental") -> pd.DataFrame:
        all_records: list[dict] = []

        for codigo in codigos:
            config = SERIES_CATALOG.get(codigo)
            if not config:
                logger.warning(f"Serie {codigo} no encontrada en catalogo")
                continue
            records = self._extract_serie(codigo, config, mode)
            all_records.extend(records)

        return pd.DataFrame(all_records) if all_records else pd.DataFrame()

    def _extract_serie(
        self, codigo: str, config: SerieConfig, mode: str
    ) -> list[dict]:
        if mode == "incremental":
            start = self._get_incremental_start(codigo)
        else:
            start = "2010-1"

        end = f"{datetime.now().year}-{datetime.now().month}"

        data = self.client.fetch_single_series(codigo, start, end)
        if not data or "periods" not in data:
            return []

        self._save_raw_response(codigo, data)

        records = []
        for period in data["periods"]:
            parsed_date = parse_bcrp_period(period["name"])
            if not parsed_date:
                continue

            raw_value = period["values"][0] if period["values"] else "n.d."
            if raw_value == "n.d." or raw_value.strip() == "":
                continue

            try:
                valor = float(raw_value.replace(",", ""))
            except (ValueError, AttributeError):
                logger.warning(f"Valor no numerico en {codigo}/{period['name']}: {raw_value}")
                continue

            records.append({
                "serie_codigo": codigo,
                "serie_nombre": config.nombre,
                "categoria": config.categoria,
                "fecha": parsed_date,
                "valor": valor,
                "unidad": config.unidad,
            })

        if records:
            last_date = max(r["fecha"] for r in records)
            self._update_control(codigo, last_date)

        return records

    def _get_incremental_start(self, codigo: str) -> str:
        last_date_str = self.control.get(codigo)
        if not last_date_str:
            return "2010-1"

        last = date.fromisoformat(last_date_str)
        next_month = last.month + 1
        next_year = last.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        return f"{next_year}-{next_month}"

    def _save_raw_response(self, codigo: str, data: dict) -> None:
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = RAW_DIR / f"{codigo}_{timestamp}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_control(self) -> dict[str, str]:
        if CONTROL_FILE.exists():
            with open(CONTROL_FILE, "r") as f:
                return json.load(f)
        return {}

    def _update_control(self, codigo: str, last_date: date) -> None:
        self.control[codigo] = last_date.isoformat()
        self._save_control()

    def _save_control(self) -> None:
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONTROL_FILE, "w") as f:
            json.dump(self.control, f, indent=2)
