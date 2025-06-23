from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from pydantic import BaseModel

from app.core.database import get_db
from app.services.question_service import create_question_service, get_questions_by_exercise, add_options_to_question, update_question_service
from app.schemas.question import QuestionCreate, QuestionOut

router = APIRouter()

class OptionsCreate(BaseModel):
    options: List[str]


@router.put("/{question_id}", response_model=QuestionOut)
async def update_question(question_id: int, question: QuestionCreate, db: AsyncSession = Depends(get_db)):
    updated = await update_question_service(db, question_id, question)
    return QuestionOut(
        id=updated.id,
        question_text=updated.question_text,
        correct_answer=updated.correct_answer,
        explanation=updated.explanation,
        order=updated.order,
        points=updated.points,
        difficulty=updated.difficulty,
        options=updated.options
    )

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
        options=question_with_options.options
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
            options=q.options
        )
        for q in questions
    ]

@router.post("/{question_id}/options", response_model=QuestionOut)
async def add_options_to_question_endpoint(
    question_id: int,
    options_data: OptionsCreate,
    db: AsyncSession = Depends(get_db)
):
    """Agrega opciones a una pregunta existente."""
    question = await add_options_to_question(db, question_id, options_data.options)
    return QuestionOut(
        id=question.id,
        question_text=question.question_text,
        correct_answer=question.correct_answer,
        explanation=question.explanation,
        order=question.order,
        points=question.points,
        difficulty=question.difficulty,
        options=question.options
    )

