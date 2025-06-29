from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class UserAnswerCreate(BaseModel):
    question_id: int
    answer_text: Optional[str] = None
    option_id: Optional[int] = None

class UserExerciseResponseCreate(BaseModel):
    exercise_id: int
    answers: List[UserAnswerCreate]

class UserAnswerRead(BaseModel):
    id: int
    question_id: int
    option_id: Optional[int]
    answer_text: Optional[str]
    is_correct: bool
    points_earned: int
    submitted_at: datetime

    class Config:
        from_attributes = True

class UserExerciseResponseRead(BaseModel):
    id: int
    user_id: int
    exercise_id: int
    submitted_at: datetime
    score: int
    is_valid: bool
    answers: List[UserAnswerRead]

    class Config:
        from_attributes = True

class AnswerFeedback(BaseModel):
    question_id: int
    question_text: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    score_percentage: int
    feedback: str
    points_earned: int
    total_points: int 