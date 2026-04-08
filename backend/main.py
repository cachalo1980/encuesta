import os
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text

import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="DevMentor Survey API", version="0.6.0")

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Autenticación básica para rutas de admin ──────────────────────────────────
# Implementación intencional mínima: un header personalizado con contraseña fija.
# ¿Por qué no JWT/OAuth2 aquí?
#   - JWT requiere un sistema de login completo (emisión de tokens, refresh, etc.)
#   - Para un MVP de acceso interno con un solo mentor, este approach es suficiente
#   - En producción real se usaría OAuth2 con Bearer tokens (FastAPI lo soporta)
# La contraseña viene de la variable de entorno ADMIN_PASSWORD del contenedor,
# nunca hardcodeada en el código fuente.
def require_admin(x_admin_password: str = Header(default=None)):
    """
    Dependencia que valida el header X-Admin-Password.
    FastAPI convierte automáticamente 'X-Admin-Password' → 'x_admin_password'
    (minúsculas, guiones → guiones bajos).
    Si la contraseña no coincide, retorna 403 Forbidden.
    """
    admin_pwd = os.getenv("ADMIN_PASSWORD", "")
    if not admin_pwd or x_admin_password != admin_pwd:
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado. Header X-Admin-Password incorrecto.",
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
    """Retorna todas las preguntas ordenadas por 'order'."""
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
    Guarda (o reemplaza) las respuestas de un mentoreado.
    Estrategia idempotente: delete + insert dentro de la misma transacción.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    db.query(models.Response).filter(models.Response.user_id == user_id).delete()

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
        db.refresh(r)
    return saved


@app.get("/users/{user_id}/responses/", response_model=List[schemas.ResponseOut])
def get_user_responses(user_id: int, db: Session = Depends(get_db)):
    """Retorna todas las respuestas de un mentoreado específico."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    return (
        db.query(models.Response)
        .filter(models.Response.user_id == user_id)
        .order_by(models.Response.question_id)
        .all()
    )


# ── Admin ─────────────────────────────────────────────────────────────────────

@app.get(
    "/admin/responses/",
    response_model=List[schemas.AdminResponseOut],
    dependencies=[Depends(require_admin)],
)
def get_all_responses(db: Session = Depends(get_db)):
    """
    Retorna todas las respuestas de todos los usuarios, enriquecidas con el
    texto de la pregunta. Usa joinedload para cargar preguntas en una sola query
    (evita el problema N+1: una query extra por cada respuesta).
    Requiere header X-Admin-Password.
    """
    responses = (
        db.query(models.Response)
        .options(joinedload(models.Response.question))
        .order_by(models.Response.user_id, models.Response.question_id)
        .all()
    )
    return [
        schemas.AdminResponseOut(
            id=r.id,
            user_id=r.user_id,
            question_id=r.question_id,
            question_text=r.question.text,
            text_answer=r.text_answer,
            scale_answer=r.scale_answer,
            evaluation=r.evaluation,
            score=r.score,
        )
        for r in responses
    ]


@app.patch(
    "/admin/responses/{response_id}/",
    response_model=schemas.AdminResponseOut,
    dependencies=[Depends(require_admin)],
)
def update_evaluation(
    response_id: int,
    update_in: schemas.EvaluationUpdate,
    db: Session = Depends(get_db),
):
    """
    Permite al mentor guardar su evaluación y puntuación sobre una respuesta.
    Solo actualiza los campos enviados (PATCH semántico: campos omitidos = sin cambio).
    Requiere header X-Admin-Password.
    """
    response = (
        db.query(models.Response)
        .options(joinedload(models.Response.question))
        .filter(models.Response.id == response_id)
        .first()
    )
    if not response:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada.")

    if update_in.evaluation is not None:
        response.evaluation = update_in.evaluation
    if update_in.score is not None:
        response.score = update_in.score

    db.commit()
    db.refresh(response)

    return schemas.AdminResponseOut(
        id=response.id,
        user_id=response.user_id,
        question_id=response.question_id,
        question_text=response.question.text,
        text_answer=response.text_answer,
        scale_answer=response.scale_answer,
        evaluation=response.evaluation,
        score=response.score,
    )
