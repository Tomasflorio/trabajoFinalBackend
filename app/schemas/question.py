from pydantic import BaseModel
from typing import Optional, List

class QuestionCreate(BaseModel):
    question_text: str
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    order: Optional[int] = 0
    options: Optional[List[str]] = []

class QuestionOut(BaseModel):
    id: int
    question_text: str
    correct_answer: Optional[str]
    explanation: Optional[str]
    order: int
    options: List[str]

    class Config:
        from_attributes = True
