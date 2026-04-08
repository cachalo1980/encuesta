-- Script de inicialización ejecutado automáticamente por PostgreSQL
-- al crear el contenedor por primera vez (directorio /docker-entrypoint-initdb.d/)

CREATE TABLE IF NOT EXISTS users (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Fila de prueba para confirmar que la tabla existe y funciona
INSERT INTO users (name) VALUES ('Admin') ON CONFLICT DO NOTHING;
