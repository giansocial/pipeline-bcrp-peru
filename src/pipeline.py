import argparse
from datetime import datetime

from src.config.settings import RAW_DIR, PROCESSED_DIR, WAREHOUSE_DIR
from src.extract.bcrp_client import BCRPClient
from src.extract.ingestion import IncrementalIngestion
from src.transform.cleaner import TimeSeriesCleaner
from src.transform.enricher import TimeSeriesEnricher
from src.transform.anomaly_detector import AnomalyDetector
from src.quality.validators import validate_dataset
from src.quality.reporter import save_quality_report, print_quality_summary
from src.load.warehouse_loader import WarehouseLoader
from src.utils.logger import setup_logger

logger = setup_logger("pipeline")


class BCRPPipeline:
    def __init__(self) -> None:
        self.client = BCRPClient()
        self.ingestion = IncrementalIngestion(self.client)
        self.cleaner = TimeSeriesCleaner()
        self.enricher = TimeSeriesEnricher()
        self.detector = AnomalyDetector()
        self.loader = WarehouseLoader()
        self.start_time = None

    def run(self, mode: str = "incremental", series: list[str] | None = None) -> None:
        self.start_time = datetime.now()
        logger.info(f"Pipeline iniciado: {self.start_time.isoformat()}")
        logger.info(f"Modo: {mode}")

        for d in (RAW_DIR, PROCESSED_DIR, WAREHOUSE_DIR):
            d.mkdir(parents=True, exist_ok=True)

        try:
            df = self._extract(mode, series)
            if df.empty:
                logger.warning("Sin datos para procesar")
                return

            df = self._transform(df)
            self._load(df)

            elapsed = (datetime.now() - self.start_time).total_seconds()
            logger.info(f"Pipeline completado en {elapsed:.1f} segundos")

        except Exception as e:
            logger.error(f"Pipeline fallido: {e}")
            raise
        finally:
            self.client.close()

    def _extract(self, mode: str, series: list[str] | None) -> "pd.DataFrame":
        logger.info("ETAPA 1: Extraccion (Bronze)")

        if series:
            df = self.ingestion.extract_series(series, mode)
        else:
            df = self.ingestion.extract_all(mode)

        if not df.empty:
            report = validate_dataset(df, name="bronze_raw")
            save_quality_report(report)
            print_quality_summary(report)

        return df

    def _transform(self, df: "pd.DataFrame") -> "pd.DataFrame":
        logger.info("ETAPA 2: Transformacion (Silver)")

        df = self.cleaner.clean(df)
        gaps = self.cleaner.detect_temporal_gaps(df)
        if not gaps.empty:
            logger.warning(f"Gaps temporales detectados:\n{gaps.to_string()}")

        df = self.enricher.enrich(df)

        report = validate_dataset(df, name="silver_enriched")
        save_quality_report(report)

        logger.info("ETAPA 2.5: Deteccion de anomalias")
        df = self.detector.detect(df)

        anomalies = df[df["es_anomalia"]]
        if not anomalies.empty:
            logger.info(f"Anomalias encontradas: {len(anomalies)}")
            for _, row in anomalies.iterrows():
                logger.info(
                    f"  {row['serie_codigo']} | {row['fecha']} | "
                    f"valor={row['valor']:.2f} | z={row['z_score']:.2f} | "
                    f"metodos: {row['metodos_anomalia']}"
                )

        return df

    def _load(self, df: "pd.DataFrame") -> None:
        logger.info("ETAPA 3: Carga (Gold)")

        self.loader.export_to_csv(df, "indicadores_economicos.csv")

        report = validate_dataset(df, name="gold_final")
        save_quality_report(report)
        print_quality_summary(report)

        logger.info(
            f"Datos exportados a {WAREHOUSE_DIR}/indicadores_economicos.csv. "
            f"Para cargar a PostgreSQL, ejecuta los scripts en sql/."
        )


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de Indicadores Macroeconomicos del Peru (BCRP)"
    )
    parser.add_argument(
        "--mode",
        choices=["full", "incremental"],
        default="incremental",
        help="Modo de ingesta: full (recarga completa) o incremental",
    )
    parser.add_argument(
        "--series",
        nargs="*",
        default=None,
        help="Codigos de series a procesar (default: todas)",
    )
    parser.add_argument(
        "--schedule",
        choices=["daily", "weekly", "monthly"],
        default=None,
        help="Ejecutar como tarea programada",
    )
    args = parser.parse_args()

    if args.schedule:
        from src.scheduler.runner import PipelineScheduler

        pipeline = BCRPPipeline()
        scheduler = PipelineScheduler(
            lambda: pipeline.run(mode="incremental"),
            interval=args.schedule,
        )
        scheduler.setup()
        scheduler.start()
    else:
        pipeline = BCRPPipeline()
        pipeline.run(mode=args.mode, series=args.series)


if __name__ == "__main__":
    main()
