import pytest
import pandas as pd
from datetime import date

from src.quality.validators import validate_dataset


def test_dataset_limpio():
    df = pd.DataFrame({
        "serie_codigo": ["A", "B", "C"],
        "fecha": [date(2023, 1, 1), date(2023, 2, 1), date(2023, 3, 1)],
        "valor": [1.0, 2.0, 3.0],
    })
    report = validate_dataset(df, name="test")
    assert report.score == 100.0
    assert report.null_count == 0
    assert report.duplicate_count == 0


def test_dataset_con_duplicados():
    df = pd.DataFrame({
        "serie_codigo": ["A", "A", "B"],
        "fecha": [date(2023, 1, 1), date(2023, 1, 1), date(2023, 2, 1)],
        "valor": [1.0, 1.0, 2.0],
    })
    report = validate_dataset(df, name="test_dup")
    assert report.duplicate_count == 1
    assert report.score < 100.0


def test_dataset_con_nulls():
    df = pd.DataFrame({
        "serie_codigo": ["A", "B", None],
        "fecha": [date(2023, 1, 1), None, date(2023, 3, 1)],
        "valor": [1.0, 2.0, 3.0],
    })
    report = validate_dataset(df, name="test_null")
    assert report.null_count == 2
    assert report.score < 100.0


def test_dataset_vacio():
    df = pd.DataFrame()
    report = validate_dataset(df, name="test_empty")
    assert report.total_rows == 0
    assert report.score == 0.0


def test_columnas_requeridas_faltantes():
    df = pd.DataFrame({"valor": [1.0]})
    report = validate_dataset(
        df, name="test_schema",
        required_columns=["valor", "fecha", "serie_codigo"],
    )
    assert report.score < 100.0
    assert "fecha" in report.details["missing_columns"]
