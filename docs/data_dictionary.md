# Diccionario de datos

## fact_indicador_economico

Tabla de hechos central. Contiene los valores mensuales de cada indicador con metricas derivadas.

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| serie_codigo | VARCHAR(20) | Codigo de la serie en el BCRP |
| fecha | DATE | Primer dia del mes |
| valor | NUMERIC(18,4) | Valor del indicador |
| variacion_mensual | NUMERIC(10,4) | Cambio porcentual respecto al mes anterior |
| variacion_anual | NUMERIC(10,4) | Cambio porcentual respecto al mismo mes del anio anterior |
| media_movil_3m | NUMERIC(18,4) | Promedio movil de 3 meses |
| media_movil_6m | NUMERIC(18,4) | Promedio movil de 6 meses |
| media_movil_12m | NUMERIC(18,4) | Promedio movil de 12 meses |
| volatilidad_12m | NUMERIC(18,4) | Desviacion estandar rolling de 12 meses |
| z_score | NUMERIC(8,4) | Z-score respecto a la media historica |
| es_anomalia | BOOLEAN | Detectada como anomalia por al menos 2 metodos |
| metodos_anomalia | VARCHAR(100) | Metodos que detectaron la anomalia |

## dim_serie

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| codigo_bcrp | VARCHAR(20) | Codigo unico de la serie |
| nombre | VARCHAR(200) | Nombre descriptivo |
| categoria | VARCHAR(50) | Clasificacion tematica |
| unidad | VARCHAR(100) | Unidad de medida |
| frecuencia | VARCHAR(20) | Frecuencia de publicacion |
| decimales | INTEGER | Precision decimal |

## dim_tiempo

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| fecha | DATE | Primer dia del mes |
| anio | INTEGER | Anio |
| mes | INTEGER | Numero de mes (1-12) |
| trimestre | INTEGER | Trimestre (1-4) |
| semestre | INTEGER | Semestre (1-2) |
| nombre_mes | VARCHAR(20) | Nombre del mes en espaniol |

## dim_categoria

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| nombre | VARCHAR(50) | Nombre de la categoria |
| descripcion | VARCHAR(200) | Descripcion de la categoria |

## Series del BCRP

| Codigo | Indicador | Categoria | Unidad |
|--------|-----------|-----------|--------|
| PN01234PM | Tipo de cambio USD/PEN | Cambiario | Soles por dolar |
| PN38705PM | IPC Lima Metropolitana | Precios | Indice Dic.2021=100 |
| PN00015MM | Credito sector privado MN | Monetario | Millones de soles |
| PN00069MM | Credito sector privado ME | Monetario | Millones de dolares |
| PN00072MM | Liquidez sistema financiero | Monetario | Millones de soles |
| PN07819NM | Tasa interes activa MN | Tasas de interes | Porcentaje |
| PN07804NM | Tasa interes pasiva MN | Tasas de interes | Porcentaje |
