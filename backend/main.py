from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import text

import models
import schemas
from database import engine, get_db

# Crea las tablas en PostgreSQL si aún no existen.
# Se ejecuta antes de instanciar FastAPI para que la DB esté lista desde el primer request.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="DevMentor Survey API", version="0.4.0")

# ── CORS ──────────────────────────────────────────────────────────────────────
# Permite que el frontend (React u otro cliente) haga peticiones al backend
# desde un origen diferente (distinto puerto o dominio).
# allow_origins=["*"] es permisivo: válido para desarrollo y MVP.
# En producción, reemplazar "*" por el dominio real del frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Utilidades ────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"db_status": "connected"}
    except Exception as e:
        return {"db_status": "error", "detail": str(e)}


# ── Usuarios ──────────────────────────────────────────────────────────────────

@app.post("/users/", response_model=schemas.UserResponse, status_code=201)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Crea un nuevo mentoreado. Retorna HTTP 400 si el email ya existe."""
    new_user = models.User(name=user_in.name, email=user_in.email)
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El email ya está registrado.")
    return new_user


@app.get("/users/", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    """Retorna la lista de todos los usuarios registrados."""
    return db.query(models.User).order_by(models.User.id).all()


# ── Preguntas ─────────────────────────────────────────────────────────────────

@app.get("/questions/", response_model=List[schemas.QuestionResponse])
def get_questions(db: Session = Depends(get_db)):
    """
    Retorna todas las preguntas del cuestionario ordenadas por 'order'.
    La tabla se puebla ejecutando: docker compose exec backend python seed.py
    """
    return db.query(models.Question).order_by(models.Question.order).all()


# ── Respuestas ────────────────────────────────────────────────────────────────

@app.post(
    "/users/{user_id}/responses/",
    response_model=List[schemas.ResponseOut],
    status_code=201,
)
def create_responses(
    user_id: int,
    responses_in: List[schemas.ResponseCreate],
    db: Session = Depends(get_db),
):
    """
    Guarda las respuestas de un mentoreado al cuestionario.
    Recibe una lista de respuestas en un solo request (envío del formulario completo).
    Retorna HTTP 404 si el usuario no existe.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    saved = []
    for r in responses_in:
        new_response = models.Response(
            user_id=user_id,
            question_id=r.question_id,
            text_answer=r.text_answer,
            scale_answer=r.scale_answer,
        )
        db.add(new_response)
        saved.append(new_response)

    db.commit()
    for r in saved:
        db.refresh(r)  # Recarga cada objeto para obtener id y created_at generados por la DB
    return saved


@app.get("/users/{user_id}/responses/", response_model=List[schemas.ResponseOut])
def get_user_responses(user_id: int, db: Session = Depends(get_db)):
    """
    Retorna todas las respuestas de un mentoreado específico.
    Permite al mentor revisar el cuestionario contestado.
    Retorna HTTP 404 si el usuario no existe.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    return (
        db.query(models.Response)
        .filter(models.Response.user_id == user_id)
        .order_by(models.Response.question_id)
        .all()
    )
