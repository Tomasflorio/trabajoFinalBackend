from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.user_exercise_response import UserExerciseResponse
from app.models.user_answer import UserAnswer
from app.models.question import Question
from app.models.option import Option
from app.schemas.exercise_response import UserExerciseResponseCreate
from typing import List
import re
import logging

# Configurar el logger
logger = logging.getLogger(__name__)

def normalize_text(text: str) -> str:
    """Normaliza el texto para comparación:
    - Convierte a minúsculas
    - Elimina espacios extra
    - Elimina puntuación
    """
    if not text:
        return ""
    # Convertir a minúsculas y eliminar espacios extra
    text = text.lower().strip()
    # Eliminar puntuación excepto en números
    text = re.sub(r'[^\w\s]', '', text)
    # Reemplazar múltiples espacios con uno solo
    text = re.sub(r'\s+', ' ', text)
    return text

def check_answer(user_answer: str, correct_answer: str) -> bool:
    """Verifica si la respuesta del usuario es correcta."""
    logger.info("\n=== Checking Answer ===")
    logger.info(f"Raw user answer: '{user_answer}'")
    logger.info(f"Raw correct answer: '{correct_answer}'")
    
    if not user_answer or not correct_answer:
        logger.info("Empty answer detected")
        return False
    
    # Convertir a minúsculas y eliminar espacios
    user_answer = user_answer.lower().strip()
    correct_answers = [ans.lower().strip() for ans in correct_answer.split('|')]
    
    logger.info(f"Normalized user answer: '{user_answer}'")
    logger.info(f"Normalized correct answers: {correct_answers}")
    
    # Verificar cada respuesta correcta
    for correct in correct_answers:
        logger.info(f"Comparing '{user_answer}' with '{correct}'")
        if user_answer == correct:
            logger.info("Match found!")
            return True
    
    logger.info("No matches found")
    return False

async def create_exercise_response(
    db: AsyncSession,
    user_id: int,
    response_data: UserExerciseResponseCreate
) -> UserExerciseResponse:
    try:
        # Crear la respuesta del ejercicio
        exercise_response = UserExerciseResponse(
            user_id=user_id,
            exercise_id=response_data.exercise_id,
            score=0,
            is_valid=False
        )
        db.add(exercise_response)
        await db.flush()

        total_score = 0
        all_correct = True

        # Procesar cada respuesta
        for answer_data in response_data.answers:
            # Obtener la pregunta
            result = await db.execute(
                select(Question).where(Question.id == answer_data.question_id)
            )
            question = result.scalar_one_or_none()
            
            if not question:
                logger.error(f"Question not found for ID: {answer_data.question_id}")
                continue

            logger.info(f"Processing question {question.id}: {question.question_text}")
            logger.info(f"Correct answer from DB: {question.correct_answer}")

            is_correct = False
            points_earned = 0

            # Si se proporcionó una opción, verificar si es correcta
            if answer_data.option_id is not None:
                result = await db.execute(
                    select(Option).where(
                        Option.id == answer_data.option_id,
                        Option.question_id == answer_data.question_id
                    )
                )
                option = result.scalar_one_or_none()
                if option:
                    is_correct = check_answer(option.option_text, question.correct_answer)
                    points_earned = question.points if is_correct else 0
                    logger.info(f"Option selected: {option.option_text}, is_correct: {is_correct}")
                else:
                    logger.error(f"Option {answer_data.option_id} not found for question {answer_data.question_id}")
                    continue
            # Si se proporcionó texto, verificar como antes
            elif answer_data.answer_text:
                is_correct = check_answer(answer_data.answer_text, question.correct_answer)
                points_earned = question.points if is_correct else 0
                logger.info(f"Text answer: {answer_data.answer_text}, is_correct: {is_correct}")
            
            logger.info(f"Answer is {'correct' if is_correct else 'incorrect'}")
            
            if not is_correct:
                all_correct = False

            # Crear la respuesta del usuario
            user_answer = UserAnswer(
                exercise_response_id=exercise_response.id,
                question_id=answer_data.question_id,
                option_id=answer_data.option_id,
                answer_text=answer_data.answer_text,
                is_correct=is_correct,
                points_earned=points_earned
            )
            db.add(user_answer)
            total_score += points_earned

        # Actualizar la puntuación total y validez
        exercise_response.score = total_score
        exercise_response.is_valid = all_correct

        await db.commit()
        
        # Recargar la respuesta con sus relaciones
        result = await db.execute(
            select(UserExerciseResponse)
            .options(selectinload(UserExerciseResponse.answers))
            .where(UserExerciseResponse.id == exercise_response.id)
        )
        return result.scalar_one()
    except Exception as e:
        logger.error(f"Error creating exercise response: {str(e)}")
        await db.rollback()
        raise

async def get_user_exercise_responses(
    db: AsyncSession,
    user_id: int
) -> List[UserExerciseResponse]:
    result = await db.execute(
        select(UserExerciseResponse)
        .options(selectinload(UserExerciseResponse.answers))
        .where(UserExerciseResponse.user_id == user_id)
        .order_by(UserExerciseResponse.submitted_at.desc())
    )
    return result.scalars().all()

async def get_exercise_response(
    db: AsyncSession,
    response_id: int
) -> UserExerciseResponse:
    result = await db.execute(
        select(UserExerciseResponse)
        .options(selectinload(UserExerciseResponse.answers))
        .where(UserExerciseResponse.id == response_id)
    )
    return result.scalar_one_or_none() 