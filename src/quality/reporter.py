import json
from datetime import datetime
from pathlib import Path

from src.config.settings import DATA_DIR
from src.quality.validators import QualityReport
from src.utils.logger import setup_logger

logger = setup_logger("quality.reporter")

REPORTS_DIR = DATA_DIR / "quality_reports"


def save_quality_report(report: QualityReport) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = REPORTS_DIR / f"quality_{report.name}_{timestamp}.json"

    data = {
        "name": report.name,
        "timestamp": report.timestamp,
        "total_rows": report.total_rows,
        "valid_rows": report.valid_rows,
        "null_count": report.null_count,
        "duplicate_count": report.duplicate_count,
        "gaps_count": report.gaps_count,
        "score": report.score,
        "details": report.details,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"Reporte guardado: {filepath}")
    return filepath


def print_quality_summary(report: QualityReport) -> None:
    print(f"\n  REPORTE DE CALIDAD: {report.name}")
    print(f"  {'-' * 40}")
    print(f"  Fecha:         {report.timestamp}")
    print(f"  Total filas:   {report.total_rows:,}")
    print(f"  Filas validas: {report.valid_rows:,}")
    print(f"  Nulls:         {report.null_count:,}")
    print(f"  Duplicados:    {report.duplicate_count:,}")
    print(f"  Score:         {report.score}%")
    print()
