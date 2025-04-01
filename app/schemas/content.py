from pydantic import BaseModel
from typing import Optional
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

# Esquema para leer un contenido
class ContentRead(BaseModel):
    id: int
    thematic: Thematic
    link: str
    title: str
    img: str

    class Config:
        from_attributes = True  # Permite convertir desde modelos de SQLAlchemy
