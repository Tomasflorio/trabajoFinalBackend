from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.services.question_service import create_question_service, get_questions_by_exercise
from app.schemas.question import QuestionCreate, QuestionOut

router = APIRouter()

@router.post("/create/{exercise_id}", response_model=QuestionOut)
async def create_question(exercise_id: int, question: QuestionCreate, db: AsyncSession = Depends(get_db)):
    created = await create_question_service(db, exercise_id, question)
    # Recarga la pregunta con las opciones usando selectinload
    result = await db.execute(
        select(created.__class__).options(selectinload(created.__class__.options)).where(created.__class__.id == created.id)
    )
    question_with_options = result.scalar_one()
    return QuestionOut(
        id=question_with_options.id,
        question_text=question_with_options.question_text,
        correct_answer=question_with_options.correct_answer,
        explanation=question_with_options.explanation,
        order=question_with_options.order,
        points=question_with_options.points,  # <-- agrega esto
        difficulty=question_with_options.difficulty,  # <-- agrega esto
        options=[opt.option_text for opt in question_with_options.options]
    )

@router.get("/list/{exercise_id}", response_model=list[QuestionOut])
async def list_questions_by_exercise(exercise_id: int, db: AsyncSession = Depends(get_db)):
    questions = await get_questions_by_exercise(db, exercise_id)
    return [
        QuestionOut(
            id=q.id,
            question_text=q.question_text,
            correct_answer=q.correct_answer,
            explanation=q.explanation,
            order=q.order,
            points=q.points,  # <-- agrega esto
            difficulty=q.difficulty,  # <-- agrega esto
            options=[opt.option_text for opt in q.options]
        )
        for q in questions
    ]