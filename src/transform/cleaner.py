import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger("transform.cleaner")


class TimeSeriesCleaner:
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        initial_rows = len(df)
        df = df.drop_duplicates(subset=["serie_codigo", "fecha"])
        dropped = initial_rows - len(df)
        if dropped > 0:
            logger.info(f"Eliminados {dropped} duplicados")

        df = df.sort_values(["serie_codigo", "fecha"]).reset_index(drop=True)

        return df

    def detect_temporal_gaps(self, df: pd.DataFrame) -> pd.DataFrame:
        gaps: list[dict] = []

        for codigo, group in df.groupby("serie_codigo"):
            dates = pd.to_datetime(group["fecha"]).sort_values()
            if len(dates) < 2:
                continue

            expected_delta = pd.DateOffset(months=1)
            for i in range(1, len(dates)):
                diff_months = (
                    (dates.iloc[i].year - dates.iloc[i - 1].year) * 12
                    + dates.iloc[i].month - dates.iloc[i - 1].month
                )
                if diff_months > 1:
                    gaps.append({
                        "serie_codigo": codigo,
                        "fecha_desde": dates.iloc[i - 1],
                        "fecha_hasta": dates.iloc[i],
                        "meses_faltantes": diff_months - 1,
                    })

        if gaps:
            logger.warning(f"Detectados {len(gaps)} gaps temporales")
        return pd.DataFrame(gaps)

    def remove_outliers_by_range(
        self, df: pd.DataFrame, column: str, min_val: float, max_val: float
    ) -> pd.DataFrame:
        df = df.copy()
        mask = (df[column] >= min_val) & (df[column] <= max_val)
        removed = (~mask).sum()
        if removed > 0:
            logger.info(f"Eliminados {removed} valores fuera de rango en {column}")
        return df[mask].reset_index(drop=True)
