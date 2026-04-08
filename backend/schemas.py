from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# ── Usuarios ──────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """Datos que el cliente debe enviar para crear un usuario."""
    name:  str
    email: EmailStr


class UserResponse(BaseModel):
    """Datos que la API devuelve al consultar un usuario."""
    id:         int
    name:       str
    email:      str
    role:       str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Preguntas ─────────────────────────────────────────────────────────────────

class QuestionBase(BaseModel):
    """Campos comunes de una pregunta (usados por herencia)."""
    text:          str
    section:       str
    question_type: str
    is_required:   bool
    order:         int


class QuestionResponse(QuestionBase):
    """Datos que la API devuelve al listar preguntas."""
    id: int

    model_config = {"from_attributes": True}


# ── Respuestas ────────────────────────────────────────────────────────────────

class ResponseCreate(BaseModel):
    """
    Datos que el cliente envía para responder una pregunta.
    Solo uno de los dos campos de respuesta debe estar presente:
    - text_answer:  para TEXT y PARAGRAPH
    - scale_answer: para LINEAR_SCALE (valores 1-10)
    """
    question_id:  int
    text_answer:  Optional[str] = None
    scale_answer: Optional[int] = None


class ResponseOut(ResponseCreate):
    """Datos que la API devuelve al leer las respuestas del cuestionario."""
    id:         int
    user_id:    int
    evaluation: Optional[str] = None   # Feedback escrito por el mentor
    score:      Optional[int] = None   # Puntuación asignada por el mentor

    model_config = {"from_attributes": True}


# ── Admin ─────────────────────────────────────────────────────────────────────

class AdminResponseOut(BaseModel):
    """
    Respuesta enriquecida para el panel de administración.
    Incluye el texto de la pregunta y el nombre del usuario (obtenidos por JOIN)
    para que el mentor no tenga que cruzar datos manualmente.
    No usa from_attributes porque se construye manualmente en el endpoint.
    """
    id:            int
    user_id:       int
    user_name:     str
    question_id:   int
    question_text: str
    text_answer:   Optional[str] = None
    scale_answer:  Optional[int] = None
    evaluation:    Optional[str] = None
    score:         Optional[int] = None


class EvaluationUpdate(BaseModel):
    """Payload para PATCH /admin/responses/{id}/. Ambos campos son opcionales."""
    evaluation: Optional[str] = None
    score:      Optional[int] = None


class ChangePasswordRequest(BaseModel):
    """Payload para PATCH /admin/change-password/."""
    new_password: str
