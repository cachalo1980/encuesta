from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import text

import models
import schemas
from database import engine, get_db

# Crea todas las tablas definidas en models.py si aún no existen en PostgreSQL.
# Equivalente al init.sql del Sprint 1, pero gestionado 100% desde Python.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="DevMentor Survey API", version="0.2.0")


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
    Crea un nuevo usuario (mentoreado).
    Retorna HTTP 400 si el email ya está registrado.
    """
    new_user = models.User(name=user_in.name, email=user_in.email)
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)  # Recarga el objeto con los valores generados por la DB (id, created_at)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El email ya está registrado.")
    return new_user


# ── Preguntas ─────────────────────────────────────────────────────────────────

@app.get("/questions/", response_model=List[schemas.QuestionResponse])
def get_questions(db: Session = Depends(get_db)):
    """
    Retorna todas las preguntas del cuestionario.
    Por ahora la tabla está vacía; se poblará en sprints futuros.
    """
    return db.query(models.Question).order_by(models.Question.order).all()
