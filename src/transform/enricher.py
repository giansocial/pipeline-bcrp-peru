import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger("transform.enricher")


class TimeSeriesEnricher:
    def enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        enriched_parts = []
        for codigo, group in df.groupby("serie_codigo"):
            group = group.sort_values("fecha").copy()
            group = self._add_variations(group)
            group = self._add_moving_averages(group)
            group = self._add_volatility(group)
            enriched_parts.append(group)

        result = pd.concat(enriched_parts, ignore_index=True)
        logger.info(f"Enriquecimiento completado: {len(result)} registros")
        return result

    def _add_variations(self, df: pd.DataFrame) -> pd.DataFrame:
        df["variacion_mensual"] = df["valor"].pct_change() * 100
        df["variacion_anual"] = df["valor"].pct_change(periods=12) * 100
        return df

    def _add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        df["media_movil_3m"] = df["valor"].rolling(window=3, min_periods=1).mean()
        df["media_movil_6m"] = df["valor"].rolling(window=6, min_periods=3).mean()
        df["media_movil_12m"] = df["valor"].rolling(window=12, min_periods=6).mean()
        return df

    def _add_volatility(self, df: pd.DataFrame) -> pd.DataFrame:
        df["volatilidad_12m"] = df["valor"].rolling(window=12, min_periods=6).std()
        return df
