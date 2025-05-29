from pydantic import BaseModel
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from typing import Optional, List
from app.schemas.question import QuestionOut

class ExerciseType(str, Enum):
    listening = "listening"
    reading = "reading"
    grammar = "grammar"
    writing = "writing"

class EnglishLevel(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"



class exerciseCreate(BaseModel):
    title: str
    type: ExerciseType
    level: EnglishLevel
    valid: bool = False
    instructions: str
    content_text: Optional[str] = None
    content_audio_url: Optional[str] = None


class CreateexerciseResponse(BaseModel):
    message: str
    exercise: dict
    status: int

class exerciseResponse(BaseModel):
    message: str
    exercise: dict
    status: int

class exerciseFullOut(BaseModel):
    id: int
    type: str
    level: str
    valid: bool
    instructions: str
    content_text: Optional[str]
    content_audio_url: Optional[str]
    questions: List[QuestionOut]

    class Config:
        from_attributes = True
