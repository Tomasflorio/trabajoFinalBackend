from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

# Enum para Thematic
class Thematic(str, Enum):
    technology = "technology"
    science = "science"
    literature = "literature"
    art = "art"

# Esquema para crear un contenido
class ContentCreate(BaseModel):
    thematic: Thematic
    link: str
    title: str
    img: str
    user_ids: Optional[List[int]] = None  # IDs de usuarios a asignar (opcional)

# Esquema para asignar usuarios a contenido
class ContentUserAssignment(BaseModel):
    content_id: int
    user_ids: List[int]

# Esquema para leer un contenido
class ContentRead(BaseModel):
    id: int
    thematic: Thematic
    link: str
    title: str
    img: str

    class Config:
        from_attributes = True  # Permite convertir desde modelos de SQLAlchemy

# Esquema para leer contenido con usuarios asignados
class ContentWithUsers(BaseModel):
    id: int
    thematic: Thematic
    link: str
    title: str
    img: str
    assigned_users: List[int]  # Lista de IDs de usuarios asignados

    class Config:
        from_attributes = True
