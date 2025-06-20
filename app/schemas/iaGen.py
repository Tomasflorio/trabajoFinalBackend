from pydantic import BaseModel

class ExerciseGenerationRequest(BaseModel):
    title: str
    english_level: str
    exercise_type: str
    prompt: str

class QuestionGenerationRequest(BaseModel):
    exercise_id: int
    quantity: int
    response_type: str
    question_difficulty: str
    exercise_id: int
    userRequested: str
