import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


def get_database_url() -> str:
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "encuesta_db")
    user = os.getenv("DB_USER", "encuesta_user")
    password = os.getenv("DB_PASSWORD", "encuesta_pass")
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


# El engine es el punto de entrada de SQLAlchemy a la base de datos.
# pool_pre_ping=True verifica que la conexión sigue viva antes de usarla.
engine = create_engine(get_database_url(), pool_pre_ping=True)

# sessionmaker crea una "fábrica" de sesiones configurada.
# autocommit=False: los cambios no se guardan solos; hay que llamar a db.commit().
# autoflush=False: los cambios no se sincronizan con la DB hasta el commit.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base es la clase padre de todos nuestros modelos ORM.
Base = declarative_base()


def get_db():
    """
    Dependencia de FastAPI que provee una sesión de DB por request.
    El bloque 'finally' garantiza que la sesión se cierre siempre,
    incluso si ocurre una excepción durante el procesamiento del request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
