from datetime import date

MONTH_MAP: dict[str, int] = {
    "Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Ago": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12,
}

MONTH_NAMES: list[str] = [
    "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def parse_bcrp_period(period_name: str) -> date | None:
    period_name = period_name.strip()

    for abbrev, month_num in MONTH_MAP.items():
        if abbrev in period_name:
            year_part = period_name.replace(abbrev + ".", "").strip()
            try:
                year = int(year_part)
                if year < 100:
                    year += 2000
                return date(year, month_num, 1)
            except (ValueError, TypeError):
                return None

    return None


def format_bcrp_period(target_date: date) -> str:
    abbrevs = list(MONTH_MAP.keys())
    return f"{abbrevs[target_date.month - 1]}.{target_date.year}"


def get_trimestre(mes: int) -> int:
    if mes < 1 or mes > 12:
        return 0
    return (mes - 1) // 3 + 1


def get_semestre(mes: int) -> int:
    if mes < 1 or mes > 12:
        return 0
    return 1 if mes <= 6 else 2


def get_nombre_mes(mes: int) -> str:
    if mes < 1 or mes > 12:
        return ""
    return MONTH_NAMES[mes]
