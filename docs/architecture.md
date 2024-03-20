# Arquitectura del Pipeline BCRP

## Diagrama de flujo

```
API BCRP (REST)       Ingesta Incremental       Transformacion           Carga
+--------------+      +------------------+      +-----------------+      +-------------+
| 7 series     | ---> | Control de       | ---> | Limpieza        | ---> | CSV/Parquet |
| mensuales    |      | estado           |      | Enriquecimiento |      | PostgreSQL  |
| 2010-2023    |      | (.etl_control)   |      | Anomalias       |      | (upsert)    |
+--------------+      +------------------+      +-----------------+      +-------------+
                             |                         |                       |
                         Bronze                    Silver                    Gold
```

## Medallion Architecture

### Bronze (Extraccion)
- Conexion a la API REST del BCRP
- Descarga de 7 series macroeconomicas mensuales
- Almacenamiento de respuestas crudas en JSON
- Control de estado para ingesta incremental
- Manejo de "n.d." y errores de la API

### Silver (Transformacion)
- Parseo del formato de fechas del BCRP ("Ene.2023")
- Eliminacion de duplicados y ordenamiento temporal
- Deteccion de gaps en las series
- Calculo de metricas derivadas:
  - Variacion mensual y anual (MoM, YoY)
  - Medias moviles (3, 6, 12 meses)
  - Volatilidad rolling (12 meses)
- Deteccion de anomalias con 3 metodos estadisticos

### Gold (Carga)
- Star Schema en PostgreSQL
- 1 tabla de hechos: fact_indicador_economico
- 3 dimensiones: dim_serie, dim_tiempo, dim_categoria
- Upsert para idempotencia
- Vistas analiticas precalculadas

## Deteccion de anomalias

Se usan tres metodos complementarios:

1. **Z-score**: |z| > 2.5
2. **IQR modificado**: fuera de [Q1 - 2*IQR, Q3 + 2*IQR]
3. **Desviacion de media movil**: > 2 sigma de la MA(12)

Una anomalia se confirma cuando al menos 2 de los 3 metodos la detectan.

## Scheduling

El pipeline soporta ejecucion programada via la libreria `schedule`:
- Modo diario, semanal o mensual
- Ingesta incremental por defecto (solo datos nuevos)
- Logs rotativos para monitoreo

## Stack

| Componente | Tecnologia |
|------------|------------|
| Lenguaje | Python 3.12 |
| API client | requests + retry |
| Procesamiento | pandas, numpy |
| Base de datos | PostgreSQL + SQLAlchemy 2.0 |
| Scheduling | schedule |
| Testing | pytest + pytest-cov |
| Visualizacion | matplotlib, seaborn |
