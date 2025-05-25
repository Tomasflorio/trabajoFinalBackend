from app.models.exercice import Exercise
from app.schemas.exercise import ExerciceCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.question import Question


async def create_exercise_router(db: AsyncSession, data: ExerciceCreate):
    new_ex = Exercise(**data.dict())
    db.add(new_ex)
    await db.commit()
    await db.refresh(new_ex)
    return new_ex

async def delete_exercise_router(db: AsyncSession, exercise_id: int):
    result = await db.execute(select(Exercise).filter_by(id=exercise_id))
    exercise = result.scalar_one_or_none()
    if not exercise:
        return None
    await db.delete(exercise)
    await db.commit()
    return True

async def update_exercise_router(db: AsyncSession, exercise_id: int, updates: dict):
    result = await db.execute(select(Exercise).filter_by(id=exercise_id))
    exercise = result.scalar_one_or_none()
    if not exercise:
        return None
    for key, value in updates.items():
        setattr(exercise, key, value)
    await db.commit()
    await db.refresh(exercise)
    return exercise

async def get_full_exercise(db: AsyncSession, exercise_id: int):
    result = await db.execute(
        select(Exercise)
        .options(
            selectinload(Exercise.questions).selectinload(Question.options)
        )
        .filter_by(id=exercise_id)
    )
    exercise = result.scalar_one_or_none()
    return exercise