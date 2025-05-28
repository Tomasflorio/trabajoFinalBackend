from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.exercise_response_service import (
    create_exercise_response,
    get_user_exercise_responses,
    get_exercise_response
)
from app.schemas.exercise_response import (
    UserExerciseResponseCreate,
    UserExerciseResponseRead
)
from typing import List

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