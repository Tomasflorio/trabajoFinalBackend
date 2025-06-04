from enum import Enum
from pydantic import BaseModel
from typing import Optional, List

class DifficultyLevel(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class OptionCreate(BaseModel):
    option_text: str
    is_correct: bool = False

class QuestionCreate(BaseModel):
    question_text: str
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    order: Optional[int] = 0
    points: int = 1
    difficulty: DifficultyLevel = DifficultyLevel.easy
    options: List[OptionCreate] = []

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
