from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.exercise_service import (
    create_exercise_router,
    delete_exercise_router,
    get_full_exercise,
    update_exercise_router
)
from app.schemas.exercise import ExerciceCreate, ExerciceFullOut, ExerciceResponse
router = APIRouter()
router = APIRouter()

@router.post("/create", response_model=ExerciceResponse)
async def create_exercise(exercise_data: ExerciceCreate, db: AsyncSession = Depends(get_db)):
    new_exercise = await create_exercise_router(db, exercise_data)
    return {
        "message": "Ejercicio creado",
        "exercise": {
            "id": new_exercise.id,
            "type": new_exercise.type.value if hasattr(new_exercise.type, "value") else str(new_exercise.type),
            "level": new_exercise.level.value if hasattr(new_exercise.level, "value") else str(new_exercise.level),
            "valid": new_exercise.valid,
            "instructions": new_exercise.instructions,
            "content_text": new_exercise.content_text,
            "content_audio_url": new_exercise.content_audio_url,
        },
        "status": 201
    }

@router.delete("/delete/{exercise_id}")
async def delete_exercise(exercise_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await delete_exercise_router(db, exercise_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return {"message": "Exercise deleted", "status": 200}

@router.put("/update/{exercise_id}")
async def update_exercise(exercise_id: int, exercise_data: ExerciceCreate, db: AsyncSession = Depends(get_db)):
    updates = exercise_data.model_dump(exclude_unset=True)
    updated = await update_exercise_router(db, exercise_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return {"message": "Exercise updated", "exercise": updated, "status": 200}

@router.get("/{exercise_id}/full", response_model=ExerciceFullOut)
async def get_exercise_with_questions(exercise_id: int, db: AsyncSession = Depends(get_db)):
    exercise = await get_full_exercise(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    return ExerciceFullOut(
        id=exercise.id,
        type=exercise.type,
        level=exercise.level,
        difficulty=getattr(exercise, "difficulty", None),
        points=getattr(exercise, "points", None),
        valid=exercise.valid,
        instructions=exercise.instructions,
        content_text=exercise.content_text,
        content_audio_url=exercise.content_audio_url,
        questions=[
            {
                "id": q.id,
                "question_text": q.question_text,
                "correct_answer": q.correct_answer,
                "explanation": q.explanation,
                "order": q.order,
                "options": [opt.option_text for opt in q.options]
            } for q in exercise.questions
        ]
    )
