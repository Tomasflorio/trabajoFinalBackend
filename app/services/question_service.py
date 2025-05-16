from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.question import Question
from app.models.option import Option
from app.schemas.question import QuestionCreate


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
