import pytest
from datetime import date

from src.utils.date_parser import (
    parse_bcrp_period,
    format_bcrp_period,
    get_trimestre,
    get_semestre,
    get_nombre_mes,
)


def test_formato_standard():
    result = parse_bcrp_period("Ene.2023")
    assert result == date(2023, 1, 1)


def test_diciembre():
    result = parse_bcrp_period("Dic.2020")
    assert result == date(2020, 12, 1)


def test_con_espacios():
    result = parse_bcrp_period("  Mar.2019  ")
    assert result == date(2019, 3, 1)


def test_anio_corto():
    result = parse_bcrp_period("Jun.15")
    assert result == date(2015, 6, 1)


def test_formato_invalido():
    result = parse_bcrp_period("InvalidMonth.2023")
    assert result is None


def test_todos_los_meses():
    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
             "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    for i, mes in enumerate(meses, 1):
        result = parse_bcrp_period(f"{mes}.2021")
        assert result == date(2021, i, 1), f"Fallo en {mes}"


def test_format_enero():
    assert format_bcrp_period(date(2023, 1, 1)) == "Ene.2023"


def test_format_diciembre():
    assert format_bcrp_period(date(2020, 12, 1)) == "Dic.2020"


@pytest.mark.parametrize("mes,expected", [
    (1, 1), (3, 1), (4, 2), (6, 2),
    (7, 3), (9, 3), (10, 4), (12, 4),
])
def test_trimestres(mes, expected):
    assert get_trimestre(mes) == expected


def test_trimestre_mes_invalido():
    assert get_trimestre(0) == 0
    assert get_trimestre(13) == 0


@pytest.mark.parametrize("mes,expected", [
    (1, 1), (6, 1), (7, 2), (12, 2),
])
def test_semestres(mes, expected):
    assert get_semestre(mes) == expected


def test_semestre_mes_invalido():
    assert get_semestre(0) == 0


def test_nombre_mes_enero():
    assert get_nombre_mes(1) == "Enero"


def test_nombre_mes_diciembre():
    assert get_nombre_mes(12) == "Diciembre"


def test_nombre_mes_invalido():
    assert get_nombre_mes(0) == ""
    assert get_nombre_mes(13) == ""
