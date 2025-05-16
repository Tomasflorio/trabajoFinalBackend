from app.models.exercice import Exercise
from app.schemas.exercice import ExerciceCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
<<<<<<< HEAD
from sqlalchemy.orm import selectinload
from app.models.question import Question
=======
>>>>>>> 7f9ccd920214f6dad2ad1ac785206ceb7efb1e58


async def create_exercice_router(db: AsyncSession, data: ExerciceCreate):
    new_ex = Exercise(**data.dict())
    db.add(new_ex)
    await db.commit()
    await db.refresh(new_ex)
    return new_ex

async def delete_exercice_router(db: AsyncSession, exercice_id: int):
    result = await db.execute(select(Exercise).filter_by(id=exercice_id))
    exercice = result.scalar_one_or_none()
    if not exercice:
        return None
    await db.delete(exercice)
    await db.commit()
    return True

async def uptade_exercice_router(db: AsyncSession, exercice_id: int, updates: dict):
    result = await db.execute(select(Exercise).filter_by(id=exercice_id))
    exercice = result.scalar_one_or_none()
    if not exercice:
        return None
    for key, value in updates.items():
        setattr(exercice, key, value)
    await db.commit()
    await db.refresh(exercice)
    return exercice

async def get_full_exercise(db: AsyncSession, exercise_id: int):
    result = await db.execute(
<<<<<<< HEAD
        select(Exercise)
        .options(
            selectinload(Exercise.questions).selectinload(Question.options)
        )
        .filter_by(id=exercise_id)
    )
    exercise = result.scalar_one_or_none()
=======
        select(Exercise).filter_by(id=exercise_id)
    )
    exercise = result.scalar_one_or_none()
    if not exercise:
        return None

    # Cargar preguntas y sus opciones (lazy loading explícito)
    await db.refresh(exercise)
    for question in exercise.questions:
        await db.refresh(question)

>>>>>>> 7f9ccd920214f6dad2ad1ac785206ceb7efb1e58
    return exercise