import numpy as np
import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger("transform.anomaly_detector")

ZSCORE_THRESHOLD = 2.5
IQR_MULTIPLIER = 2.0
MA_DEVIATION_SIGMA = 2.0
MIN_METHODS_FOR_CONFIRMED = 2


class AnomalyDetector:
    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["anomaly_zscore"] = False
        df["anomaly_iqr"] = False
        df["anomaly_ma"] = False
        df["es_anomalia"] = False
        df["z_score"] = np.nan
        df["metodos_anomalia"] = ""

        results = []
        for codigo, group in df.groupby("serie_codigo"):
            group = self._detect_zscore(group)
            group = self._detect_iqr(group)
            group = self._detect_moving_avg_deviation(group)
            group = self._combine_methods(group)
            results.append(group)

        result = pd.concat(results, ignore_index=True)

        total_anomalies = result["es_anomalia"].sum()
        logger.info(
            f"Deteccion completada: {total_anomalies} anomalias confirmadas "
            f"de {len(result)} registros ({total_anomalies/len(result)*100:.1f}%)"
        )
        return result

    def _detect_zscore(self, df: pd.DataFrame) -> pd.DataFrame:
        mean = df["valor"].mean()
        std = df["valor"].std()

        if std == 0:
            df["z_score"] = 0.0
            return df

        df["z_score"] = (df["valor"] - mean) / std
        df["anomaly_zscore"] = df["z_score"].abs() > ZSCORE_THRESHOLD
        return df

    def _detect_iqr(self, df: pd.DataFrame) -> pd.DataFrame:
        q1 = df["valor"].quantile(0.25)
        q3 = df["valor"].quantile(0.75)
        iqr = q3 - q1

        lower = q1 - IQR_MULTIPLIER * iqr
        upper = q3 + IQR_MULTIPLIER * iqr

        df["anomaly_iqr"] = (df["valor"] < lower) | (df["valor"] > upper)
        return df

    def _detect_moving_avg_deviation(self, df: pd.DataFrame) -> pd.DataFrame:
        if "media_movil_12m" not in df.columns or "volatilidad_12m" not in df.columns:
            return df

        deviation = (df["valor"] - df["media_movil_12m"]).abs()
        threshold = MA_DEVIATION_SIGMA * df["volatilidad_12m"]

        valid_mask = df["media_movil_12m"].notna() & df["volatilidad_12m"].notna()
        df.loc[valid_mask, "anomaly_ma"] = deviation[valid_mask] > threshold[valid_mask]
        return df

    def _combine_methods(self, df: pd.DataFrame) -> pd.DataFrame:
        method_count = (
            df["anomaly_zscore"].astype(int)
            + df["anomaly_iqr"].astype(int)
            + df["anomaly_ma"].astype(int)
        )

        df["es_anomalia"] = method_count >= MIN_METHODS_FOR_CONFIRMED

        methods_list = []
        for _, row in df.iterrows():
            active = []
            if row["anomaly_zscore"]:
                active.append("zscore")
            if row["anomaly_iqr"]:
                active.append("iqr")
            if row["anomaly_ma"]:
                active.append("moving_avg")
            methods_list.append(",".join(active))

        df["metodos_anomalia"] = methods_list
        return df
