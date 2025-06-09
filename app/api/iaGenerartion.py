from fastapi import APIRouter, HTTPException, Body, Depends
from app.services.ia_generation_service import generate_exercise, generate_question
from app.schemas.iaGen import ExerciseGenerationRequest, QuestionGenerationRequest
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


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

@router.post("/generate_question")
async def generate_question_endpoint(
    genData: QuestionGenerationRequest = Body(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        question = await generate_question(
            exercise_id=genData.exercise_id,
            cantidad=genData.quantity,
            response_type=genData.response_type,
            question_difficulty=genData.question_difficulty,
            userRequested=genData.userRequested,
            db=db
        )
        return {"message": "Question generated successfully", "question": question}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))