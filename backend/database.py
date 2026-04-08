import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Una sola variable de entorno con la URL completa de conexión.
# Formato: postgresql://usuario:password@host:puerto/nombre_db
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://encuesta_user:encuesta_pass@localhost:5432/encuesta_db"
)

# El engine es el punto de entrada de SQLAlchemy a la base de datos.
# pool_pre_ping=True verifica que la conexión sigue viva antes de usarla,
# evitando errores silenciosos por conexiones idle que PostgreSQL cerró.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# sessionmaker crea una "fábrica" de sesiones configurada.
# autocommit=False: los cambios no se guardan solos; hay que llamar a db.commit().
# autoflush=False: los objetos no se sincronizan con la DB hasta el commit.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base es la clase padre de todos los modelos ORM.
# SQLAlchemy usa sus metadatos para generar/inspeccionar el esquema de la DB.
Base = declarative_base()


def get_db():
    """
    Dependencia de FastAPI: provee una sesión de DB por request y la cierra siempre.
    FastAPI inyecta esta función en los endpoints que la declaren con Depends(get_db).
    El bloque 'finally' garantiza el cierre incluso si el endpoint lanza una excepción.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
