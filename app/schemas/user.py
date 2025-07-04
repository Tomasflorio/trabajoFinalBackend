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

class LoginRequest(BaseModel):
    email: str
    password: str

# Esquemas para recupero de contraseña
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ValidateTokenRequest(BaseModel):
    token: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class PasswordResetResponse(BaseModel):
    message: str
    status: int

    
# Esquema para leer un usuario (sin contraseña por seguridad)
class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    points: int
    isAdmin: bool
    englishLevel: EnglishLevel

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    isAdmin: bool  # Asegúrate de incluir los campos necesarios

    class Config:
        from_attributes = True  # Permite convertir desde modelos de SQLAlchemy

class RegisterResponse(BaseModel):
    message: str
    user: UserResponse
    status: int

    class Config:
        from_attributes = True