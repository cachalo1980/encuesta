from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Datos que el cliente debe enviar para crear un usuario."""
    name:  str
    email: EmailStr  # Pydantic valida automáticamente el formato del email


class UserResponse(BaseModel):
    """Datos que la API devuelve al consultar un usuario."""
    id:         int
    name:       str
    email:      str
    role:       str
    created_at: datetime

    model_config = {"from_attributes": True}
    # from_attributes=True (antes orm_mode=True en Pydantic v1) permite que
    # Pydantic lea los datos desde atributos de un objeto ORM, no solo desde dicts.
