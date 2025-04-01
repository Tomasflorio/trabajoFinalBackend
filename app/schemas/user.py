from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class EnglishLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

# Esquema para la creación de un usuario (sin ID porque la BD lo genera)
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str  # La contraseña se enviará como texto plano antes de ser hasheada
    points: Optional[int] = 0
    isAdmin: bool
    englishLevel: EnglishLevel

# Esquema para leer un usuario (sin contraseña por seguridad)
class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    points: int
    isAdmin: bool
    englishLevel: EnglishLevel

    class Config:
        from_attributes = True  # Permite convertir desde modelos de SQLAlchemy