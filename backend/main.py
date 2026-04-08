import os
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text

import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="DevMentor Survey API", version="0.7.0")

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Contraseña admin en memoria ───────────────────────────────────────────────
# Se inicializa desde la variable de entorno al arrancar el contenedor.
# Al cambiarla via PATCH /admin/change-password/ se actualiza solo en este proceso:
# persiste mientras el contenedor vive y se resetea al reiniciar.
#
# ¿Por qué no en la DB? Para este MVP de acceso interno es suficiente.
# En producción: guardarla en DB hasheada con bcrypt, nunca en texto plano.
_admin_password: str = os.getenv("ADMIN_PASSWORD", "")


def require_admin(x_admin_password: str = Header(default=None)):
    """
    Dependencia que valida el header X-Admin-Password contra _admin_password.
    FastAPI convierte automáticamente 'X-Admin-Password' → 'x_admin_password'
    (minúsculas, guiones → guiones bajos).
    Si la contraseña no coincide, retorna 403 Forbidden.
    """
    if not _admin_password or x_admin_password != _admin_password:
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
    """
    Crea un nuevo mentoreado o retorna el existente si el email ya está registrado.
    Estrategia upsert-by-email: el mentoreado puede recargar la página sin perder su sesión.
    """
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        return existing
    new_user = models.User(name=user_in.name, email=user_in.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
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
        .options(joinedload(models.Response.question), joinedload(models.Response.user))
        .order_by(models.Response.user_id, models.Response.question_id)
        .all()
    )
    return [
        schemas.AdminResponseOut(
            id=r.id,
            user_id=r.user_id,
            user_name=r.user.name,
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
        .options(joinedload(models.Response.question), joinedload(models.Response.user))
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
        user_name=response.user.name,
        question_id=response.question_id,
        question_text=response.question.text,
        text_answer=response.text_answer,
        scale_answer=response.scale_answer,
        evaluation=response.evaluation,
        score=response.score,
    )


@app.patch(
    "/admin/change-password/",
    dependencies=[Depends(require_admin)],
)
def change_admin_password(body: schemas.ChangePasswordRequest):
    """
    Cambia la contraseña de administrador en memoria.
    Requiere la contraseña actual en el header X-Admin-Password.
    La nueva contraseña vive en este proceso hasta que el contenedor se reinicie;
    al reiniciar vuelve al valor de ADMIN_PASSWORD del docker-compose.yml.
    """
    global _admin_password
    if not body.new_password or not body.new_password.strip():
        raise HTTPException(status_code=422, detail="La nueva contraseña no puede estar vacía.")
    _admin_password = body.new_password
    return {"detail": "Contraseña actualizada correctamente."}
