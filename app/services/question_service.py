from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.question import Question
from app.models.option import Option
from app.schemas.question import QuestionCreate
from typing import List
from sqlalchemy.orm import selectinload


async def create_question_service(db: AsyncSession, exercise_id: int, question_data: QuestionCreate):
    new_question = Question(
        exercise_id=exercise_id,
        question_text=question_data.question_text,
        correct_answer=question_data.correct_answer,
        explanation=question_data.explanation,
        order=question_data.order
    )
    db.add(new_question)
    await db.commit()
    await db.refresh(new_question)

    # Agregar opciones si hay
    for opt_text in question_data.options:
        new_option = Option(question_id=new_question.id, option_text=opt_text)
        db.add(new_option)

    await db.commit()
    # Refresca la pregunta para que tenga las opciones cargadas
    await db.refresh(new_question)
    return new_question

async def get_questions_by_exercise(db: AsyncSession, exercise_id: int):
    result = await db.execute(
        select(Question).filter_by(exercise_id=exercise_id).order_by(Question.order)
    )
    return result.scalars().all()

async def add_options_to_question(db: AsyncSession, question_id: int, options: List[str]):
    """Agrega opciones a una pregunta existente."""
    for opt_text in options:
        new_option = Option(question_id=question_id, option_text=opt_text)
        db.add(new_option)
    
    await db.commit()
    
    # Recargar la pregunta con sus opciones
    result = await db.execute(
        select(Question)
        .options(selectinload(Question.options))
        .where(Question.id == question_id)
    )
    return result.scalar_one()

async def update_question_service(db: AsyncSession, question_id: int, question_data: QuestionCreate):
    result = await db.execute(select(Question).filter_by(id=question_id))
    question = result.scalar_one_or_none()
    if not question:
        return None
    for key, value in question_data.model_dump(exclude_unset=True).items():
        setattr(question, key, value)
    await db.commit()
    await db.refresh(question)
    return question