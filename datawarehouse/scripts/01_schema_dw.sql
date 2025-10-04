-- ============================================
-- DATA WAREHOUSE - MODELO DIMENSIONAL
-- ============================================

-- DIMENSIÓN: País
CREATE TABLE dim_pais (
    pais_id SERIAL PRIMARY KEY,
    codigo VARCHAR(2) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    moneda VARCHAR(3)
);

INSERT INTO dim_pais (codigo, nombre, moneda) VALUES
('GT', 'Guatemala', 'GTQ'),
('SV', 'El Salvador', 'USD');

-- DIMENSIÓN: Tiempo
CREATE TABLE dim_tiempo (
    tiempo_id SERIAL PRIMARY KEY,
    fecha DATE UNIQUE NOT NULL,
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    dia INTEGER NOT NULL,
    dia_semana INTEGER NOT NULL,
    es_fin_semana BOOLEAN NOT NULL
);

-- Generar 3 años de fechas
INSERT INTO dim_tiempo (fecha, anio, mes, dia, dia_semana, es_fin_semana)
SELECT 
    fecha::DATE,
    EXTRACT(YEAR FROM fecha)::INTEGER,
    EXTRACT(MONTH FROM fecha)::INTEGER,
    EXTRACT(DAY FROM fecha)::INTEGER,
    EXTRACT(ISODOW FROM fecha)::INTEGER,
    CASE WHEN EXTRACT(ISODOW FROM fecha) IN (6,7) THEN TRUE ELSE FALSE END
FROM generate_series(
    CURRENT_DATE - INTERVAL '3 years',
    CURRENT_DATE + INTERVAL '1 year',
    '1 day'::INTERVAL
) AS fecha;

-- DIMENSIÓN: Película
CREATE TABLE dim_pelicula (
    pelicula_id SERIAL PRIMARY KEY,
    titulo VARCHAR(200),
    genero VARCHAR(50),
    clasificacion VARCHAR(10),
    duracion_minutos INTEGER
);

-- DIMENSIÓN: Sucursal
CREATE TABLE dim_sucursal (
    sucursal_id SERIAL PRIMARY KEY,
    pais_id INTEGER REFERENCES dim_pais(pais_id),
    nombre VARCHAR(100),
    ciudad VARCHAR(100)
);

-- TABLA DE HECHOS: Ventas
CREATE TABLE fact_ventas (
    venta_id SERIAL PRIMARY KEY,
    tiempo_id INTEGER REFERENCES dim_tiempo(tiempo_id),
    pelicula_id INTEGER REFERENCES dim_pelicula(pelicula_id),
    sucursal_id INTEGER REFERENCES dim_sucursal(sucursal_id),
    pais_id INTEGER REFERENCES dim_pais(pais_id),
    
    -- Métricas
    cantidad_boletos INTEGER NOT NULL,
    ingreso_total NUMERIC(12,2) NOT NULL,
    precio_promedio NUMERIC(10,2),
    
    -- Metadatos
    fuente VARCHAR(10),
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX idx_fact_ventas_tiempo ON fact_ventas(tiempo_id);
CREATE INDEX idx_fact_ventas_pelicula ON fact_ventas(pelicula_id);
CREATE INDEX idx_fact_ventas_pais ON fact_ventas(pais_id);
CREATE INDEX idx_fact_ventas_fecha ON fact_ventas(tiempo_id, pais_id);
