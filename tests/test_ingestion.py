import pytest
import json
from datetime import date
from unittest.mock import MagicMock, patch

import pandas as pd

from src.extract.ingestion import IncrementalIngestion


MOCK_RESPONSE = {
    "config": {
        "title": "Tipo de cambio",
        "series": [{"name": "TC venta", "dec": "3"}],
    },
    "periods": [
        {"name": "Ene.2023", "values": ["3.812"]},
        {"name": "Feb.2023", "values": ["3.795"]},
        {"name": "Mar.2023", "values": ["n.d."]},
        {"name": "Abr.2023", "values": ["3.750"]},
    ],
}


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.fetch_single_series.return_value = MOCK_RESPONSE.copy()
    return client


@pytest.fixture
def ingestion(mock_client, tmp_path):
    with patch("src.extract.ingestion.RAW_DIR", tmp_path), \
         patch("src.extract.ingestion.CONTROL_FILE", tmp_path / ".etl_control.json"):
        ing = IncrementalIngestion(client=mock_client)
        yield ing


def test_extrae_valores_validos(ingestion, mock_client, tmp_path):
    with patch("src.extract.ingestion.RAW_DIR", tmp_path), \
         patch("src.extract.ingestion.CONTROL_FILE", tmp_path / ".etl_control.json"):
        df = ingestion.extract_series(["PN01234PM"], mode="full")
    assert len(df) == 3


def test_descarta_nd(ingestion, mock_client, tmp_path):
    with patch("src.extract.ingestion.RAW_DIR", tmp_path), \
         patch("src.extract.ingestion.CONTROL_FILE", tmp_path / ".etl_control.json"):
        df = ingestion.extract_series(["PN01234PM"], mode="full")
    values = df["valor"].tolist()
    assert all(isinstance(v, float) for v in values)


def test_parsea_fechas_correctamente(ingestion, mock_client, tmp_path):
    with patch("src.extract.ingestion.RAW_DIR", tmp_path), \
         patch("src.extract.ingestion.CONTROL_FILE", tmp_path / ".etl_control.json"):
        df = ingestion.extract_series(["PN01234PM"], mode="full")
    fechas = df["fecha"].tolist()
    assert date(2023, 1, 1) in fechas
    assert date(2023, 2, 1) in fechas


def test_serie_no_existente(ingestion):
    df = ingestion.extract_series(["FAKE_CODE"], mode="full")
    assert df.empty


def test_respuesta_vacia(ingestion, mock_client, tmp_path):
    mock_client.fetch_single_series.return_value = {}
    with patch("src.extract.ingestion.RAW_DIR", tmp_path), \
         patch("src.extract.ingestion.CONTROL_FILE", tmp_path / ".etl_control.json"):
        df = ingestion.extract_series(["PN01234PM"], mode="full")
    assert df.empty
