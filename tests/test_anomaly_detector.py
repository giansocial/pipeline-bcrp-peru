import pytest
import pandas as pd
import numpy as np
from datetime import date

from src.transform.anomaly_detector import AnomalyDetector


@pytest.fixture
def detector():
    return AnomalyDetector()


@pytest.fixture
def series_with_spike():
    dates = [date(2020, m, 1) for m in range(1, 13)]
    dates += [date(2021, m, 1) for m in range(1, 13)]
    values = [3.5, 3.4, 3.6, 3.5, 3.5, 3.4, 3.6, 3.5, 3.4, 3.5, 3.6, 3.5,
              3.4, 3.5, 3.6, 3.5, 3.4, 3.5, 3.5, 3.6, 3.4, 3.5, 3.5, 8.0]
    return pd.DataFrame({
        "serie_codigo": ["TEST"] * 24,
        "fecha": dates,
        "valor": values,
        "media_movil_12m": [3.5] * 24,
        "volatilidad_12m": [0.1] * 24,
    })


@pytest.fixture
def stable_series():
    dates = [date(2020, m, 1) for m in range(1, 13)]
    return pd.DataFrame({
        "serie_codigo": ["STABLE"] * 12,
        "fecha": dates,
        "valor": [3.50, 3.51, 3.49, 3.52, 3.48, 3.50,
                  3.51, 3.49, 3.52, 3.48, 3.50, 3.51],
        "media_movil_12m": [3.50] * 12,
        "volatilidad_12m": [0.02] * 12,
    })


def test_detecta_spike_como_anomalia(detector, series_with_spike):
    result = detector.detect(series_with_spike)
    anomalias = result[result["es_anomalia"]]
    assert len(anomalias) >= 1
    assert anomalias.iloc[-1]["valor"] == 8.0


def test_serie_estable_sin_anomalias(detector, stable_series):
    result = detector.detect(stable_series)
    assert result["es_anomalia"].sum() == 0


def test_agrega_z_score(detector, series_with_spike):
    result = detector.detect(series_with_spike)
    assert "z_score" in result.columns
    assert result["z_score"].notna().all()


def test_metodos_anomalia_no_vacio(detector, series_with_spike):
    result = detector.detect(series_with_spike)
    anomalias = result[result["es_anomalia"]]
    for _, row in anomalias.iterrows():
        assert len(row["metodos_anomalia"]) > 0


def test_requiere_dos_metodos_minimo(detector, series_with_spike):
    result = detector.detect(series_with_spike)
    anomalias = result[result["es_anomalia"]]
    for _, row in anomalias.iterrows():
        methods = row["metodos_anomalia"].split(",")
        assert len(methods) >= 2


def test_multiples_series(detector):
    df = pd.DataFrame({
        "serie_codigo": ["A"] * 12 + ["B"] * 12,
        "fecha": [date(2020, m, 1) for m in range(1, 13)] * 2,
        "valor": [1.0] * 11 + [100.0] + [5.0] * 12,
        "media_movil_12m": [1.0] * 12 + [5.0] * 12,
        "volatilidad_12m": [0.1] * 12 + [0.1] * 12,
    })
    result = detector.detect(df)
    a_anomalies = result[(result["serie_codigo"] == "A") & result["es_anomalia"]]
    b_anomalies = result[(result["serie_codigo"] == "B") & result["es_anomalia"]]
    assert len(a_anomalies) >= 1
    assert len(b_anomalies) == 0
