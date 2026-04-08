from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean,
    DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(255), nullable=False)
    email      = Column(String(255), unique=True, nullable=False, index=True)
    role       = Column(String(50), nullable=False, default="mentoreado")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relación inversa: acceder a user.responses devuelve todas sus respuestas
    responses  = relationship("Response", back_populates="user")


class Question(Base):
    __tablename__ = "questions"

    id            = Column(Integer, primary_key=True, index=True)
    section       = Column(String(255), nullable=False)
    question_type = Column(String(50), nullable=False)   # ej: "text", "scale", "multiple_choice"
    text          = Column(Text, nullable=False)
    is_required   = Column(Boolean, default=True, nullable=False)
    order         = Column(Integer, nullable=False)

    responses     = relationship("Response", back_populates="question")


class Response(Base):
    __tablename__ = "responses"

    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id    = Column(Integer, ForeignKey("questions.id"), nullable=False)
    text_answer    = Column(Text, nullable=True)          # Para respuestas de texto libre
    scale_answer   = Column(Integer, nullable=True)       # Para respuestas 1-10
    evaluation     = Column(Text, nullable=True)          # Feedback escrito por el mentor
    score          = Column(Integer, nullable=True)       # Puntuación asignada por el mentor (1-10)
    created_at     = Column(DateTime, default=datetime.utcnow, nullable=False)

    user           = relationship("User", back_populates="responses")
    question       = relationship("Question", back_populates="responses")
