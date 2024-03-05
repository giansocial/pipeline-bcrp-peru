import re

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.config.database import create_db_engine
from src.utils.logger import setup_logger

logger = setup_logger("load.warehouse_loader")

VALID_TABLE_PATTERN = re.compile(r"^[a-z_][a-z0-9_]*$")


class WarehouseLoader:
    def __init__(self, engine: Engine | None = None) -> None:
        self.engine = engine or create_db_engine()

    def upsert_indicators(self, df: pd.DataFrame) -> int:
        table = "fact_indicador_economico"
        self._validate_table_name(table)

        if df.empty:
            return 0

        columns = [
            "serie_codigo", "fecha", "valor", "variacion_mensual",
            "variacion_anual", "media_movil_3m", "media_movil_6m",
            "media_movil_12m", "volatilidad_12m", "z_score",
            "es_anomalia", "metodos_anomalia",
        ]

        available = [c for c in columns if c in df.columns]
        subset = df[available].copy()

        subset["fecha"] = pd.to_datetime(subset["fecha"])

        col_list = ", ".join(available)
        placeholders = ", ".join(f":{c}" for c in available)
        update_set = ", ".join(
            f"{c} = EXCLUDED.{c}" for c in available
            if c not in ("serie_codigo", "fecha")
        )

        query = text(
            f"INSERT INTO {table} ({col_list}) VALUES ({placeholders}) "
            f"ON CONFLICT (serie_codigo, fecha) DO UPDATE SET {update_set}"
        )

        with self.engine.begin() as conn:
            for _, row in subset.iterrows():
                params = {c: row[c] for c in available}
                conn.execute(query, params)

        logger.info(f"Upsert completado: {len(subset)} registros en {table}")
        return len(subset)

    def load_dimensions(self, df: pd.DataFrame) -> None:
        self._load_dim_serie(df)
        self._load_dim_tiempo(df)

    def _load_dim_serie(self, df: pd.DataFrame) -> None:
        table = "dim_serie"
        self._validate_table_name(table)

        if "serie_codigo" not in df.columns:
            return

        series = df[["serie_codigo", "serie_nombre", "categoria", "unidad"]].drop_duplicates()

        query = text(
            f"INSERT INTO {table} (codigo_bcrp, nombre, categoria, unidad) "
            f"VALUES (:codigo, :nombre, :categoria, :unidad) "
            f"ON CONFLICT (codigo_bcrp) DO NOTHING"
        )

        with self.engine.begin() as conn:
            for _, row in series.iterrows():
                conn.execute(query, {
                    "codigo": row["serie_codigo"],
                    "nombre": row["serie_nombre"],
                    "categoria": row["categoria"],
                    "unidad": row["unidad"],
                })

        logger.info(f"Dimensiones de serie cargadas: {len(series)} registros")

    def _load_dim_tiempo(self, df: pd.DataFrame) -> None:
        table = "dim_tiempo"
        self._validate_table_name(table)

        if "fecha" not in df.columns:
            return

        from src.utils.date_parser import get_nombre_mes, get_trimestre, get_semestre

        dates = pd.to_datetime(df["fecha"]).dt.date.unique()

        query = text(
            f"INSERT INTO {table} (fecha, anio, mes, trimestre, semestre, nombre_mes) "
            f"VALUES (:fecha, :anio, :mes, :trimestre, :semestre, :nombre_mes) "
            f"ON CONFLICT (fecha) DO NOTHING"
        )

        with self.engine.begin() as conn:
            for d in dates:
                conn.execute(query, {
                    "fecha": d,
                    "anio": d.year,
                    "mes": d.month,
                    "trimestre": get_trimestre(d.month),
                    "semestre": get_semestre(d.month),
                    "nombre_mes": get_nombre_mes(d.month),
                })

        logger.info(f"Dimensiones de tiempo cargadas: {len(dates)} fechas")

    def export_to_csv(self, df: pd.DataFrame, filename: str) -> None:
        from src.config.settings import WAREHOUSE_DIR
        WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)
        filepath = WAREHOUSE_DIR / filename
        df.to_csv(filepath, index=False, encoding="utf-8")
        logger.info(f"Exportado: {filepath}")

    def _validate_table_name(self, table_name: str) -> str:
        if not VALID_TABLE_PATTERN.match(table_name):
            raise ValueError(f"Nombre de tabla invalido: {table_name}")
        return table_name
