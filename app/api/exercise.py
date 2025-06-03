from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.exercise_service import (
    create_exercise_router,
    create_full_exercise_router,
    delete_exercise_router,
    get_full_exercise,
    update_exercise_router,
    get_all_exercises,
    get_exercises_by_type_router
)
from app.schemas.exercise import (
    exerciseCreate,
    exerciseResponse,
    CreateexerciseResponse
)
from typing import List
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class ExerciseWrapper(BaseModel):
    exercise: exerciseCreate

router = APIRouter()

@router.post("/create", response_model=CreateexerciseResponse)
async def create_exercise(exercise_data: exerciseCreate, db: AsyncSession = Depends(get_db)):
    new_exercise = await create_exercise_router(db, exercise_data)
    return {
        "message": "Ejercicio creado",
        "exercise": {  
            "id": new_exercise.id,
            "title": new_exercise.title,
            "type": new_exercise.type.value if hasattr(new_exercise.type, "value") else str(new_exercise.type),
            "level": new_exercise.level.value if hasattr(new_exercise.level, "value") else str(new_exercise.level),
            "valid": new_exercise.valid,
            "instructions": new_exercise.instructions,
            "content_text": new_exercise.content_text,
            "content_audio_url": new_exercise.content_audio_url,
        },
        "status": 201
    }

@router.post("/create/full", response_model=exerciseResponse)
async def create_exercise_full(exercise_data: exerciseCreate, db: AsyncSession = Depends(get_db)):
    try:
        logger.info("Iniciando creación de ejercicio completo")
        new_exercise = await create_full_exercise_router(db, exercise_data)
        logger.info("Ejercicio completo creado exitosamente")
        
        return {
            "message": "Ejercicio completo creado exitosamente",
            "exercise": {
                "id": new_exercise.id,
                "title": new_exercise.title,
                "type": new_exercise.type.value if hasattr(new_exercise.type, "value") else str(new_exercise.type),
                "level": new_exercise.level.value if hasattr(new_exercise.level, "value") else str(new_exercise.level),
                "valid": new_exercise.valid,
                "instructions": new_exercise.instructions,
                "content_text": new_exercise.content_text,
                "content_audio_url": new_exercise.content_audio_url,
                "questions": [
                    {
                        "id": q.id,
                        "question_text": q.question_text,
                        "correct_answer": q.correct_answer,
                        "explanation": q.explanation,
                        "order": q.order,
                        "points": q.points,
                        "difficulty": q.difficulty,
                        "options": [
                            {
                                "id": o.id,
                                "option_text": o.option_text,
                                "is_correct": o.is_correct
                            } for o in q.options
                        ]
                    } for q in new_exercise.questions
                ]
            },
            "status": 201
        }
    except Exception as e:
        logger.error(f"Error al crear ejercicio completo: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el ejercicio completo: {str(e)}"
        )

@router.delete("/{exercise_id}")
async def delete_exercise(exercise_id: int, db: AsyncSession = Depends(get_db)):
    result = await delete_exercise_router(db, exercise_id)
    if not result:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return {"message": "Exercise deleted successfully"}

@router.put("/{exercise_id}", response_model=exerciseResponse)
async def update_exercise(exercise_id: int, updates: dict, db: AsyncSession = Depends(get_db)):
    updated_exercise = await update_exercise_router(db, exercise_id, updates)
    if not updated_exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return updated_exercise

@router.get("/{exercise_id}", response_model=exerciseResponse)
async def get_exercise(exercise_id: int, db: AsyncSession = Depends(get_db)):
    exercise = await get_full_exercise(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise

@router.get("/", response_model=List[exerciseResponse])
async def get_exercises(db: AsyncSession = Depends(get_db)):
    exercises = await get_all_exercises(db)
    return exercises

@router.get("/bytype/{exercise_type}", response_model=List[exerciseResponse])
async def get_exercises_by_type(exercise_type: str, db: AsyncSession = Depends(get_db)):
    exercises = await get_exercises_by_type_router(db, exercise_type)
    return exercises

