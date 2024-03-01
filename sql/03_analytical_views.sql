CREATE OR REPLACE VIEW v_anomalias_por_serie AS
SELECT
    f.serie_codigo,
    s.nombre AS serie_nombre,
    s.categoria,
    COUNT(*) AS total_anomalias,
    MIN(f.fecha) AS primera_anomalia,
    MAX(f.fecha) AS ultima_anomalia,
    AVG(ABS(f.z_score)) AS z_score_promedio
FROM fact_indicador_economico f
JOIN dim_serie s ON f.serie_codigo = s.codigo_bcrp
WHERE f.es_anomalia = TRUE
GROUP BY f.serie_codigo, s.nombre, s.categoria
ORDER BY total_anomalias DESC;

CREATE OR REPLACE VIEW v_resumen_mensual AS
SELECT
    t.anio,
    t.mes,
    t.nombre_mes,
    f.serie_codigo,
    s.nombre AS serie_nombre,
    f.valor,
    f.variacion_mensual,
    f.variacion_anual,
    f.media_movil_12m,
    f.es_anomalia
FROM fact_indicador_economico f
JOIN dim_tiempo t ON f.fecha = t.fecha
JOIN dim_serie s ON f.serie_codigo = s.codigo_bcrp
ORDER BY t.anio, t.mes, f.serie_codigo;

CREATE OR REPLACE VIEW v_volatilidad_anual AS
SELECT
    EXTRACT(YEAR FROM f.fecha) AS anio,
    f.serie_codigo,
    s.nombre AS serie_nombre,
    AVG(f.valor) AS valor_promedio,
    STDDEV(f.valor) AS desviacion_estandar,
    MIN(f.valor) AS valor_minimo,
    MAX(f.valor) AS valor_maximo,
    MAX(f.valor) - MIN(f.valor) AS rango,
    COUNT(*) FILTER (WHERE f.es_anomalia) AS anomalias_en_anio
FROM fact_indicador_economico f
JOIN dim_serie s ON f.serie_codigo = s.codigo_bcrp
GROUP BY EXTRACT(YEAR FROM f.fecha), f.serie_codigo, s.nombre
ORDER BY anio, f.serie_codigo;
