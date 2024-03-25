from dataclasses import dataclass
from datetime import date
from enum import Enum


class AnomalyMethod(Enum):
    ZSCORE = "zscore"
    IQR = "iqr"
    MOVING_AVG = "moving_avg"


@dataclass(frozen=True)
class RawPeriod:
    name: str
    values: list[str]


@dataclass(frozen=True)
class IndicatorRecord:
    serie_codigo: str
    fecha: date
    valor: float
    variacion_mensual: float | None = None
    variacion_anual: float | None = None
    media_movil_3m: float | None = None
    media_movil_6m: float | None = None
    media_movil_12m: float | None = None
    volatilidad_12m: float | None = None
    z_score: float | None = None
    es_anomalia: bool = False
    metodos_anomalia: str = ""


@dataclass(frozen=True)
class ETLRunLog:
    serie_codigo: str
    fecha_inicio: str
    fecha_fin: str
    registros_nuevos: int
    registros_actualizados: int
    duracion_segundos: float
    estado: str
    error: str | None = None
