import os
from fastapi import FastAPI
from sqlalchemy import create_engine, text

app = FastAPI(title="DevMentor Survey API", version="0.1.0")


def get_database_url() -> str:
    """Construye la URL de conexión a PostgreSQL desde variables de entorno."""
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "encuesta_db")
    user = os.getenv("DB_USER", "encuesta_user")
    password = os.getenv("DB_PASSWORD", "encuesta_pass")
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


@app.get("/health")
def health_check():
    """Endpoint de salud: confirma que la API está levantada y respondiendo."""
    return {"status": "ok"}


@app.get("/db-check")
def db_check():
    """
    Endpoint de verificación de DB: intenta abrir una conexión real a PostgreSQL
    y ejecuta una consulta mínima. Útil para diagnosticar problemas de red o credenciales.
    """
    try:
        engine = create_engine(get_database_url())
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"db_status": "connected"}
    except Exception as e:
        return {"db_status": "error", "detail": str(e)}
