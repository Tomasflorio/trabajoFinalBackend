from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.exercice_service import (
    create_exercice_router,
    delete_exercice_router,
    get_full_exercise,
    uptade_exercice_router
)
from app.schemas.exercice import ExerciceCreate, ExerciceFullOut, ExerciceResponse
router = APIRouter()
router = APIRouter()

@router.post("/create", response_model=ExerciceResponse)
async def create_exercice(exercice_data: ExerciceCreate, db: AsyncSession = Depends(get_db)):
    new_exercice = await create_exercice_router(db, exercice_data)
    # Convierte el objeto SQLAlchemy a dict usando Pydantic
    return {
        "message": "Ejercicio creado",
        "exercice": {
            "id": new_exercice.id,
            "type": new_exercice.type.value if hasattr(new_exercice.type, "value") else str(new_exercice.type),
            "level": new_exercice.level.value if hasattr(new_exercice.level, "value") else str(new_exercice.level),
            "difficulty": new_exercice.difficulty.value if hasattr(new_exercice.difficulty, "value") else str(new_exercice.difficulty),
            "points": new_exercice.points,
            "valid": new_exercice.valid,
            "instructions": new_exercice.instructions,
            "content_text": new_exercice.content_text,
            "content_audio_url": new_exercice.content_audio_url,
        },
        "status": 201
    }

@router.delete("/delete/{exercice_id}")
async def delete_exercice(exercice_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await delete_exercice_router(db, exercice_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Exercice not found")
    return {"message": "Exercice deleted", "status": 200}

@router.put("/update/{exercice_id}")
async def update_exercice(exercice_id: int, exercice_data: ExerciceCreate, db: AsyncSession = Depends(get_db)):
    updates = exercice_data.model_dump(exclude_unset=True)
    updated = await uptade_exercice_router(db, exercice_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Exercice not found")
    return {"message": "Exercice updated", "exercice": updated, "status": 200}

@router.get("/{exercise_id}/full", response_model=ExerciceFullOut)
async def get_exercise_with_questions(exercise_id: int, db: AsyncSession = Depends(get_db)):
    exercise = await get_full_exercise(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    return ExerciceFullOut(
        id=exercise.id,
        type=exercise.type,
        level=exercise.level,
        difficulty=exercise.difficulty,
        points=exercise.points,
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
