import pytest
import pandas as pd
from datetime import date

from src.transform.cleaner import TimeSeriesCleaner


@pytest.fixture
def cleaner():
    return TimeSeriesCleaner()


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "serie_codigo": ["PN01234PM"] * 5 + ["PN38705PM"] * 3,
        "fecha": [
            date(2023, 1, 1), date(2023, 2, 1), date(2023, 3, 1),
            date(2023, 4, 1), date(2023, 2, 1),
            date(2023, 1, 1), date(2023, 2, 1), date(2023, 3, 1),
        ],
        "valor": [3.82, 3.79, 3.75, 3.80, 3.79, 128.5, 129.1, 130.0],
    })


def test_elimina_duplicados(cleaner, sample_df):
    result = cleaner.clean(sample_df)
    assert len(result) == 7


def test_ordena_por_serie_y_fecha(cleaner, sample_df):
    result = cleaner.clean(sample_df)
    for codigo in result["serie_codigo"].unique():
        fechas = result[result["serie_codigo"] == codigo]["fecha"].tolist()
        assert fechas == sorted(fechas)


def test_detect_temporal_gaps(cleaner):
    df = pd.DataFrame({
        "serie_codigo": ["PN01234PM"] * 4,
        "fecha": [
            date(2023, 1, 1), date(2023, 2, 1),
            date(2023, 5, 1), date(2023, 6, 1),
        ],
        "valor": [3.82, 3.79, 3.75, 3.80],
    })
    gaps = cleaner.detect_temporal_gaps(df)
    assert len(gaps) == 1
    assert gaps.iloc[0]["meses_faltantes"] == 2


def test_sin_gaps(cleaner):
    df = pd.DataFrame({
        "serie_codigo": ["PN01234PM"] * 3,
        "fecha": [
            date(2023, 1, 1), date(2023, 2, 1), date(2023, 3, 1),
        ],
        "valor": [3.82, 3.79, 3.75],
    })
    gaps = cleaner.detect_temporal_gaps(df)
    assert len(gaps) == 0


def test_remove_outliers_by_range(cleaner):
    df = pd.DataFrame({
        "valor": [3.5, 3.8, -1.0, 100.0, 3.9],
    })
    result = cleaner.remove_outliers_by_range(df, "valor", 0, 10)
    assert len(result) == 3
