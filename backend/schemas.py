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
    """Datos que la API devuelve al listar preguntas. Hereda todos los campos de QuestionBase."""
    id: int

    model_config = {"from_attributes": True}
    # La herencia evita repetir los 5 campos de QuestionBase. QuestionResponse
    # solo añade lo que la DB genera: el id asignado automáticamente.


# ── Respuestas ────────────────────────────────────────────────────────────────

class ResponseCreate(BaseModel):
    """
    Datos que el cliente envía para responder una pregunta.
    Solo uno de los dos campos de respuesta debe estar presente según el tipo de pregunta:
    - text_answer:  para TEXT y PARAGRAPH
    - scale_answer: para LINEAR_SCALE (valores 1-10)
    """
    question_id:  int
    text_answer:  Optional[str] = None
    scale_answer: Optional[int] = None


class ResponseOut(ResponseCreate):
    """Datos que la API devuelve al leer las respuestas. Hereda de ResponseCreate."""
    id:      int
    user_id: int

    model_config = {"from_attributes": True}
