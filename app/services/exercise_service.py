from app.models.exercise import Exercise
from app.schemas.exercise import exerciseCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.question import Question


async def create_exercise_router(db: AsyncSession, data: exerciseCreate):
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

async def get_all_exercises(db: AsyncSession):
    result = await db.execute(
        select(Exercise)
        .options(selectinload(Exercise.questions).selectinload(Question.options))
        .order_by(Exercise.id)
    )
    exercises = result.scalars().all()
    
    # Convertir los ejercicios al formato esperado
    formatted_exercises = []
    for exercise in exercises:
        formatted_questions = []
        for question in exercise.questions:
            formatted_questions.append({
                'id': question.id,
                'question_text': question.question_text,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation,
                'order': question.order,
                'points': question.points,
                'difficulty': question.difficulty,
                'options': [opt.option_text for opt in question.options]  # Convertir objetos Option a strings
            })
        
        formatted_exercises.append({
            'id': exercise.id,
            'type': exercise.type.value,
            'level': exercise.level.value,
            'valid': exercise.valid,
            'instructions': exercise.instructions,
            'content_text': exercise.content_text,
            'content_audio_url': exercise.content_audio_url,
            'questions': formatted_questions
        })
    
    return formatted_exercises