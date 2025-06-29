from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.exercise_response_service import (
    create_exercise_response,
    get_user_exercise_responses,
    get_exercise_response,
    update_user_level,
    get_answer_feedback
)
from app.services.ia_generation_service import analyze_text_response
from app.schemas.exercise_response import (
    UserExerciseResponseCreate,
    UserExerciseResponseRead,
    AnswerFeedback
)
from app.schemas.question import QuestionOut
from typing import List
from pydantic import BaseModel

class TextResponseAnalysis(BaseModel):
    question_text: str
    correct_answer: str
    user_answer: str
    explanation: str = None

class AnalysisResult(BaseModel):
    is_correct: bool
    score_percentage: int
    feedback: str

router = APIRouter()

@router.post("/responses", response_model=UserExerciseResponseRead)
async def submit_exercise_response(
    user_id: int,
    response_data: UserExerciseResponseCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Enviar las respuestas de un ejercicio
    """
    response = await create_exercise_response(db, user_id, response_data)
    if not response:
        raise HTTPException(status_code=400, detail="Error al procesar las respuestas")
    return response

@router.get("/responses/user/{user_id}", response_model=List[UserExerciseResponseRead])
async def get_user_responses(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener todas las respuestas de un usuario
    """
    responses = await get_user_exercise_responses(db, user_id)
    return responses

@router.get("/responses/setuserlevel/{user_id}")
async def set_user_level_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Establecer el nivel de un usuario
    """
    user = await update_user_level(db, user_id)
    return {"message": "Nivel de inglés actualizado", "englishLevel": user.englishLevel}

@router.get("/responses/{response_id}", response_model=UserExerciseResponseRead)
async def get_response(
    response_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener una respuesta específica
    """
    response = await get_exercise_response(db, response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    return response

@router.get("/responses/{response_id}/feedback/{question_id}", response_model=AnswerFeedback)
async def get_response_feedback(
    response_id: int,
    question_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener feedback detallado de una respuesta específica.
    Para preguntas sin opciones, re-analiza la respuesta con IA.
    """
    feedback = await get_answer_feedback(db, response_id, question_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Respuesta o pregunta no encontrada")
    return feedback

@router.post("/analyze-text-response", response_model=AnalysisResult)
async def analyze_text_response_endpoint(
    analysis_data: TextResponseAnalysis,
    db: AsyncSession = Depends(get_db)
):
    """
    Analizar una respuesta de texto libre en tiempo real usando IA.
    """
    try:
        result = await analyze_text_response(
            question_text=analysis_data.question_text,
            correct_answer=analysis_data.correct_answer,
            user_answer=analysis_data.user_answer,
            explanation=analysis_data.explanation
        )
        return AnalysisResult(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al analizar la respuesta: {str(e)}") 