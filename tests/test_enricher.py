import pytest
import pandas as pd
import numpy as np
from datetime import date

from src.transform.enricher import TimeSeriesEnricher


@pytest.fixture
def enricher():
    return TimeSeriesEnricher()


@pytest.fixture
def monthly_series():
    dates = [date(2022, m, 1) for m in range(1, 13)]
    dates += [date(2023, m, 1) for m in range(1, 13)]
    values = [
        3.38, 3.40, 3.42, 3.45, 3.50, 3.55,
        3.60, 3.65, 3.70, 3.75, 3.80, 3.85,
        3.82, 3.79, 3.75, 3.80, 3.85, 3.90,
        3.92, 3.88, 3.84, 3.80, 3.78, 3.76,
    ]
    return pd.DataFrame({
        "serie_codigo": ["PN01234PM"] * 24,
        "fecha": dates,
        "valor": values,
    })


def test_agrega_variacion_mensual(enricher, monthly_series):
    result = enricher.enrich(monthly_series)
    assert "variacion_mensual" in result.columns
    assert pd.isna(result.iloc[0]["variacion_mensual"])
    assert not pd.isna(result.iloc[1]["variacion_mensual"])


def test_agrega_variacion_anual(enricher, monthly_series):
    result = enricher.enrich(monthly_series)
    assert "variacion_anual" in result.columns
    first_12 = result.iloc[:12]["variacion_anual"]
    assert first_12.isna().all()


def test_agrega_medias_moviles(enricher, monthly_series):
    result = enricher.enrich(monthly_series)
    assert "media_movil_3m" in result.columns
    assert "media_movil_6m" in result.columns
    assert "media_movil_12m" in result.columns


def test_agrega_volatilidad(enricher, monthly_series):
    result = enricher.enrich(monthly_series)
    assert "volatilidad_12m" in result.columns


def test_multiples_series(enricher):
    df = pd.DataFrame({
        "serie_codigo": ["A"] * 5 + ["B"] * 5,
        "fecha": [date(2023, m, 1) for m in range(1, 6)] * 2,
        "valor": [1, 2, 3, 4, 5, 10, 20, 30, 40, 50],
    })
    result = enricher.enrich(df)
    assert len(result) == 10
    a_data = result[result["serie_codigo"] == "A"]
    assert pd.isna(a_data.iloc[0]["variacion_mensual"])
