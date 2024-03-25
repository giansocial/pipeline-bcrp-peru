from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger("quality.validators")


@dataclass
class QualityReport:
    name: str
    timestamp: str
    total_rows: int
    valid_rows: int
    null_count: int
    duplicate_count: int
    gaps_count: int
    score: float
    details: dict = field(default_factory=dict)


def validate_dataset(
    df: pd.DataFrame,
    name: str,
    required_columns: list[str] | None = None,
) -> QualityReport:
    total = len(df)
    if total == 0:
        return QualityReport(
            name=name,
            timestamp=datetime.now().isoformat(),
            total_rows=0,
            valid_rows=0,
            null_count=0,
            duplicate_count=0,
            gaps_count=0,
            score=0.0,
        )

    null_count = int(df.isnull().sum().sum())
    total_cells = total * len(df.columns)
    null_ratio = null_count / total_cells if total_cells > 0 else 0

    dup_count = 0
    if "serie_codigo" in df.columns and "fecha" in df.columns:
        dup_count = int(df.duplicated(subset=["serie_codigo", "fecha"]).sum())

    dup_ratio = dup_count / total if total > 0 else 0

    missing_cols = []
    if required_columns:
        missing_cols = [c for c in required_columns if c not in df.columns]

    completeness = 1.0 - null_ratio
    uniqueness = 1.0 - dup_ratio
    schema_score = 1.0 if not missing_cols else (1.0 - len(missing_cols) / len(required_columns))

    score = round((completeness * 0.4 + uniqueness * 0.3 + schema_score * 0.3) * 100, 1)

    valid_rows = total - dup_count

    report = QualityReport(
        name=name,
        timestamp=datetime.now().isoformat(),
        total_rows=total,
        valid_rows=valid_rows,
        null_count=null_count,
        duplicate_count=dup_count,
        gaps_count=0,
        score=score,
        details={
            "completeness": round(completeness * 100, 1),
            "uniqueness": round(uniqueness * 100, 1),
            "schema_compliance": round(schema_score * 100, 1),
            "missing_columns": missing_cols,
        },
    )

    logger.info(
        f"[{name}] Calidad: {score}% | Filas: {total} | "
        f"Nulls: {null_count} | Duplicados: {dup_count}"
    )
    return report
