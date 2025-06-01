from pydantic import BaseModel

class ExerciseGenerationRequest(BaseModel):
    title: str
    english_level: str
    exercise_type: str
    prompt: str