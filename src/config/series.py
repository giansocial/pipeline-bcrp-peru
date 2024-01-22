from dataclasses import dataclass


@dataclass(frozen=True)
class SerieConfig:
    codigo: str
    nombre: str
    categoria: str
    unidad: str
    decimales: int


SERIES_CATALOG: dict[str, SerieConfig] = {
    "PN01234PM": SerieConfig(
        codigo="PN01234PM",
        nombre="Tipo de cambio promedio del periodo - venta",
        categoria="Cambiario",
        unidad="Soles por dolar",
        decimales=3,
    ),
    "PN38705PM": SerieConfig(
        codigo="PN38705PM",
        nombre="Indice de precios al consumidor de Lima Metropolitana",
        categoria="Precios",
        unidad="Indice Dic.2021=100",
        decimales=2,
    ),
    "PN00015MM": SerieConfig(
        codigo="PN00015MM",
        nombre="Credito al sector privado - moneda nacional",
        categoria="Monetario",
        unidad="Millones de soles",
        decimales=0,
    ),
    "PN00069MM": SerieConfig(
        codigo="PN00069MM",
        nombre="Credito al sector privado - moneda extranjera",
        categoria="Monetario",
        unidad="Millones de dolares",
        decimales=0,
    ),
    "PN00072MM": SerieConfig(
        codigo="PN00072MM",
        nombre="Liquidez del sistema financiero",
        categoria="Monetario",
        unidad="Millones de soles",
        decimales=0,
    ),
    "PN07819NM": SerieConfig(
        codigo="PN07819NM",
        nombre="Tasa de interes activa promedio - moneda nacional",
        categoria="Tasas de interes",
        unidad="Porcentaje",
        decimales=2,
    ),
    "PN07804NM": SerieConfig(
        codigo="PN07804NM",
        nombre="Tasa de interes pasiva promedio - moneda nacional",
        categoria="Tasas de interes",
        unidad="Porcentaje",
        decimales=2,
    ),
}

ALL_SERIES_CODES = list(SERIES_CATALOG.keys())
