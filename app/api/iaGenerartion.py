from fastapi import APIRouter, HTTPException, Body
from app.services.ia_generation_service import generate_exercise
from app.models.iaGen import ExerciseGenerationRequest

router = APIRouter()

@router.post("/generate_exercise")
async def generate_exercise_endpoint(
    genData: ExerciseGenerationRequest = Body(...)
):
    try:
        exercise = await generate_exercise(
            genData.exercise_type,
            genData.english_level,
            genData.title,
            genData.prompt
        )
        return {"message": "Exercise generated successfully", "exercise": exercise}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

