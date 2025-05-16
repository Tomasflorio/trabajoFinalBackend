from pydantic import BaseModel
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from typing import Optional, List
from app.schemas.question import QuestionOut  # Asegurate de importar esto

class ExerciseType(str, Enum):
    listening = "Listening"
    reading = "ReadingComprehension"
    grammar = "Grammar"
    writing = "Writing"

class EnglishLevel(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

class DifficultyLevel(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class ExerciceCreate(BaseModel):
    type: ExerciseType
    level: EnglishLevel
    difficulty: DifficultyLevel
    points: int
    valid: bool = False
    instructions: str
    content_text: Optional[str] = None
    content_audio_url: Optional[str] = None


class CreateExerciceResponse(BaseModel):
    message: str
    exercice: dict
    status: int

class ExerciceResponse(BaseModel):
    message: str
    exercice: dict
    status: int

class ExerciceFullOut(BaseModel):
    id: int
    type: str
    level: str
    difficulty: str
    points: int
    valid: bool
    instructions: str
    content_text: Optional[str]
    content_audio_url: Optional[str]
    questions: List[QuestionOut]

    class Config:
        from_attributes = True
