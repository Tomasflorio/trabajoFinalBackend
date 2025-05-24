from pydantic import BaseModel
from typing import Optional, List
from app.schemas.exercice import DifficultyLevel

class QuestionCreate(BaseModel):
    question_text: str
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    order: Optional[int] = 0
    points: int = 1
    difficulty: DifficultyLevel = DifficultyLevel.easy
    options: Optional[List[str]] = []

class QuestionOut(BaseModel):
    id: int
    question_text: str
    correct_answer: Optional[str]
    explanation: Optional[str]
    order: int
    points: int
    difficulty: DifficultyLevel
    options: List[str]

    class Config:
        from_attributes = True
