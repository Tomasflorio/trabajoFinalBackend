from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
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
        order=question_data.order,
        points=question_data.points,
        difficulty=question_data.difficulty
    )
    db.add(new_question)
    await db.commit()
    await db.refresh(new_question)

    # Agregar opciones si hay
    for option_data in question_data.options:
        new_option = Option(
            question_id=new_question.id, 
            option_text=option_data.option_text,
            is_correct=option_data.is_correct
        )
        db.add(new_option)

    await db.commit()
    # Refresca la pregunta para que tenga las opciones cargadas
    await db.refresh(new_question)
    return new_question

async def get_questions_by_exercise(db: AsyncSession, exercise_id: int):
    result = await db.execute(
        select(Question)
        .options(selectinload(Question.options))
        .filter_by(exercise_id=exercise_id)
        .order_by(Question.order)
    )
    return result.scalars().all()

async def add_options_to_question(db: AsyncSession, question_id: int, options: List[str]):
    """Agrega opciones a una pregunta existente."""
    for opt_text in options:
        new_option = Option(
            question_id=question_id, 
            option_text=opt_text,
            is_correct=False  # Por defecto no es correcta
        )
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
    
    # Extraer los datos de la pregunta excluyendo las opciones
    question_update_data = question_data.model_dump(exclude_unset=True, exclude={'options'})
    
    # Actualizar los campos de la pregunta
    for key, value in question_update_data.items():
        setattr(question, key, value)
    
    # Manejar las opciones por separado si se proporcionan
    if question_data.options:
        # Eliminar opciones existentes
        await db.execute(delete(Option).filter_by(question_id=question_id))
        
        # Agregar nuevas opciones
        for option_data in question_data.options:
            new_option = Option(
                question_id=question_id,
                option_text=option_data.option_text,
                is_correct=option_data.is_correct
            )
            db.add(new_option)
    
    await db.commit()
    await db.refresh(question)
    
    # Cargar las opciones para el retorno
    result = await db.execute(
        select(Question)
        .options(selectinload(Question.options))
        .where(Question.id == question_id)
    )
    return result.scalar_one()