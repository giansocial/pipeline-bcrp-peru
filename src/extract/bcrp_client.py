import time
from typing import Any

import requests

from src.config.settings import (
    BCRP_BASE_URL,
    BCRP_DEFAULT_END,
    BCRP_DEFAULT_START,
    BCRP_MAX_RETRIES,
    BCRP_RATE_LIMIT_SECONDS,
    BCRP_REQUEST_TIMEOUT,
    BCRP_RETRY_BACKOFF,
)
from src.utils.logger import setup_logger

logger = setup_logger("extract.bcrp_client")


class BCRPClient:
    def __init__(self) -> None:
        self._last_request_time: float = 0
        self._session = requests.Session()

    def fetch_series(
        self,
        series_codes: list[str],
        start: str = BCRP_DEFAULT_START,
        end: str = BCRP_DEFAULT_END,
    ) -> dict[str, Any]:
        codes_param = "-".join(series_codes)
        url = f"{BCRP_BASE_URL}/{codes_param}/json/{start}/{end}"

        self._respect_rate_limit()

        for attempt in range(1, BCRP_MAX_RETRIES + 1):
            try:
                response = self._session.get(url, timeout=BCRP_REQUEST_TIMEOUT)
                response.raise_for_status()
                data = response.json()
                logger.info(
                    f"Series {codes_param}: {len(data.get('periods', []))} periodos"
                )
                return data

            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    wait = BCRP_RETRY_BACKOFF ** attempt * 2
                    logger.warning(f"Rate limited, esperando {wait:.0f}s")
                    time.sleep(wait)
                    continue
                logger.error(f"HTTP {response.status_code} en intento {attempt}: {e}")

            except requests.exceptions.ConnectionError as e:
                logger.error(f"Error de conexion en intento {attempt}: {e}")

            except requests.exceptions.Timeout:
                logger.error(f"Timeout en intento {attempt}")

            except requests.exceptions.JSONDecodeError as e:
                logger.error(f"JSON invalido en intento {attempt}: {e}")
                return {}

            if attempt < BCRP_MAX_RETRIES:
                wait = BCRP_RETRY_BACKOFF ** attempt
                logger.info(f"Reintentando en {wait:.0f}s...")
                time.sleep(wait)

        logger.error(f"Fallaron todos los intentos para {codes_param}")
        return {}

    def fetch_single_series(
        self,
        series_code: str,
        start: str = BCRP_DEFAULT_START,
        end: str = BCRP_DEFAULT_END,
    ) -> dict[str, Any]:
        return self.fetch_series([series_code], start, end)

    def _respect_rate_limit(self) -> None:
        elapsed = time.time() - self._last_request_time
        if elapsed < BCRP_RATE_LIMIT_SECONDS:
            time.sleep(BCRP_RATE_LIMIT_SECONDS - elapsed)
        self._last_request_time = time.time()

    def close(self) -> None:
        self._session.close()
