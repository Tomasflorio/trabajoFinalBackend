from pydantic import BaseModel
from typing import Optional
from enum import Enum

# Enum para ExerciceType
class ExerciceType(str, Enum):
    LISTENING = "LISTENING"
    WRITING = "WRITING"
    READING_COMPREHENTION = "READING COMPREHENTION"
    GRAMMAR = "GRAMMAR"
   
# Enum para EnglishLevel
class EnglishLevel(str, Enum):
    A1 = 'A1'
    A2 = 'A2'
    B1 = 'B1'
    B2 = 'B2'
    C1 = 'C1'
    C2 = 'C2'


# Esquema para crear un ejercicio
class ExerciceCreate(BaseModel):
    type: ExerciceType
    response: str
    content: str
    valid: bool
    value: Optional[int] = 0
    level: EnglishLevel

class ExerciceResponse(BaseModel):
    id: int
    type: ExerciceType
    response: str
    content: str
    valid: bool
    value: int
    level: EnglishLevel

class CreateExerciceResponse(BaseModel):
    message: str
    exercice: ExerciceResponse
    status: int
