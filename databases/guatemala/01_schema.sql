-- Schema Base de Datos Guatemala
CREATE TABLE peliculas (
    pelicula_id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    genero VARCHAR(50) NOT NULL,
    duracion_minutos INTEGER NOT NULL,
    clasificacion VARCHAR(10) NOT NULL,
    director VARCHAR(100),
    fecha_estreno DATE,
    precio_base DECIMAL(10,2) NOT NULL,
    es_3d BOOLEAN DEFAULT FALSE,
    activa BOOLEAN DEFAULT TRUE,
    pais VARCHAR(2) DEFAULT 'GT',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sucursales (
    sucursal_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    direccion TEXT NOT NULL,
    numero_salas INTEGER NOT NULL,
    capacidad_total INTEGER NOT NULL,
    activa BOOLEAN DEFAULT TRUE,
    pais VARCHAR(2) DEFAULT 'GT'
);

CREATE TABLE salas (
    sala_id SERIAL PRIMARY KEY,
    sucursal_id INTEGER REFERENCES sucursales(sucursal_id),
    numero_sala INTEGER NOT NULL,
    capacidad INTEGER NOT NULL,
    tipo_sala VARCHAR(20) DEFAULT 'STANDARD',
    activa BOOLEAN DEFAULT TRUE
);

CREATE TABLE clientes (
    cliente_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    telefono VARCHAR(20),
    fecha_nacimiento DATE,
    tipo_cliente VARCHAR(20) DEFAULT 'REGULAR',
    pais VARCHAR(2) DEFAULT 'GT'
);

CREATE TABLE funciones (
    funcion_id SERIAL PRIMARY KEY,
    pelicula_id INTEGER REFERENCES peliculas(pelicula_id),
    sala_id INTEGER REFERENCES salas(sala_id),
    sucursal_id INTEGER REFERENCES sucursales(sucursal_id),
    fecha_funcion DATE NOT NULL,
    hora_funcion TIME NOT NULL,
    precio_boleto DECIMAL(10,2) NOT NULL,
    boletos_disponibles INTEGER NOT NULL,
    boletos_vendidos INTEGER DEFAULT 0,
    estado VARCHAR(20) DEFAULT 'PROGRAMADA'
);

CREATE TABLE ventas (
    venta_id SERIAL PRIMARY KEY,
    funcion_id INTEGER REFERENCES funciones(funcion_id),
    cliente_id INTEGER REFERENCES clientes(cliente_id),
    cantidad_boletos INTEGER NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    metodo_pago VARCHAR(20) NOT NULL,
    tipo_venta VARCHAR(20) DEFAULT 'TAQUILLA',
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pais VARCHAR(2) DEFAULT 'GT'
);

-- Índices
CREATE INDEX idx_funciones_fecha ON funciones(fecha_funcion);
CREATE INDEX idx_ventas_fecha ON ventas(fecha_venta);
