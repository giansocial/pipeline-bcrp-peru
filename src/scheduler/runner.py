import time
from datetime import datetime

import schedule

from src.utils.logger import setup_logger

logger = setup_logger("scheduler.runner")


class PipelineScheduler:
    def __init__(self, pipeline_fn, interval: str = "daily") -> None:
        self.pipeline_fn = pipeline_fn
        self.interval = interval
        self._running = False

    def setup(self) -> None:
        if self.interval == "daily":
            schedule.every().day.at("06:00").do(self._execute)
        elif self.interval == "weekly":
            schedule.every().monday.at("06:00").do(self._execute)
        elif self.interval == "monthly":
            schedule.every(30).days.at("06:00").do(self._execute)
        else:
            raise ValueError(f"Intervalo no soportado: {self.interval}")

        logger.info(f"Scheduler configurado: {self.interval}")

    def start(self) -> None:
        self._running = True
        logger.info("Scheduler iniciado")

        while self._running:
            schedule.run_pending()
            time.sleep(60)

    def stop(self) -> None:
        self._running = False
        logger.info("Scheduler detenido")

    def run_once(self) -> None:
        self._execute()

    def _execute(self) -> None:
        start = datetime.now()
        logger.info(f"Ejecucion programada iniciada: {start.isoformat()}")

        try:
            self.pipeline_fn()
            elapsed = (datetime.now() - start).total_seconds()
            logger.info(f"Ejecucion completada en {elapsed:.1f}s")
        except Exception as e:
            logger.error(f"Ejecucion fallida: {e}")
