CREATE TABLE IF NOT EXISTS dim_serie (
    id SERIAL PRIMARY KEY,
    codigo_bcrp varchar(20) UNIQUE NOT NULL,
    nombre varchar(200) NOT NULL,
    categoria varchar(50) NOT NULL,
    unidad varchar(100) NOT NULL,
    frecuencia varchar(20) DEFAULT 'Mensual',
    decimales INTEGER DEFAULT 2,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_tiempo (
    id SERIAL PRIMARY KEY,
    fecha DATE UNIQUE NOT NULL,
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    semestre INTEGER NOT NULL,
    nombre_mes varchar(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_categoria (
    id SERIAL PRIMARY KEY,
    nombre varchar(50) UNIQUE NOT NULL,
    descripcion varchar(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fact_indicador_economico (
    id SERIAL PRIMARY KEY,
    serie_codigo varchar(20) NOT NULL,
    fecha DATE NOT NULL,
    valor NUMERIC(18, 4) NOT NULL,
    variacion_mensual NUMERIC(10, 4),
    variacion_anual NUMERIC(10, 4),
    media_movil_3m NUMERIC(18, 4),
    media_movil_6m NUMERIC(18, 4),
    media_movil_12m NUMERIC(18, 4),
    volatilidad_12m NUMERIC(18, 4),
    z_score NUMERIC(8, 4),
    es_anomalia BOOLEAN DEFAULT FALSE,
    metodos_anomalia varchar(100) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (serie_codigo, fecha)
);

CREATE INDEX IF NOT EXISTS idx_fact_serie ON fact_indicador_economico(serie_codigo);
CREATE INDEX IF NOT EXISTS idx_fact_fecha ON fact_indicador_economico(fecha);
CREATE INDEX IF NOT EXISTS idx_fact_anomalia ON fact_indicador_economico(es_anomalia)
    WHERE es_anomalia = TRUE;
CREATE INDEX IF NOT EXISTS idx_dim_tiempo_anio_mes ON dim_tiempo(anio, mes);

-- TODO: agregar indice compuesto despues
