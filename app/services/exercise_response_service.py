from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.user_exercise_response import UserExerciseResponse
from app.models.user_answer import UserAnswer
from app.models.question import Question
from app.models.option import Option
from app.models.user import User
from app.schemas.exercise_response import UserExerciseResponseCreate
from app.services.ia_generation_service import analyze_text_response
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
            # Obtener la pregunta con sus opciones
            result = await db.execute(
                select(Question)
                .options(selectinload(Question.options))
                .where(Question.id == answer_data.question_id)
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
            # Si se proporcionó texto, verificar si la pregunta tiene opciones
            elif answer_data.answer_text:
                # Si la pregunta no tiene opciones, usar análisis de IA
                if not question.options:
                    logger.info("Question has no options, using AI analysis")
                    ai_analysis = await analyze_text_response(
                        question_text=question.question_text,
                        correct_answer=question.correct_answer,
                        user_answer=answer_data.answer_text,
                        explanation=question.explanation
                    )
                    is_correct = ai_analysis["is_correct"]
                    # Calcular puntos basados en el porcentaje de acierto
                    points_earned = int((ai_analysis["score_percentage"] / 100) * question.points)
                    logger.info(f"AI analysis result: {ai_analysis}")
                else:
                    # Si tiene opciones pero el usuario respondió texto, usar comparación básica
                    is_correct = check_answer(answer_data.answer_text, question.correct_answer)
                    points_earned = question.points if is_correct else 0
                    logger.info(f"Text answer with options available: {answer_data.answer_text}, is_correct: {is_correct}")
            
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

async def update_user_level(
    db: AsyncSession,
    user_id: int
):
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return None
        
    # Obtener la última respuesta del usuario
    user_points_query = await db.execute(
        select(UserExerciseResponse)
        .where(UserExerciseResponse.user_id == user_id)
        .order_by(UserExerciseResponse.submitted_at.desc())
    )
    total_points = user_points_query.scalars().all()
    total_points = sum(response.score for response in total_points)
    
    
    if not total_points:
        return user
        
    points = total_points
    
    if points <= 300:
        user.englishLevel = 'A1'
    elif points <= 600:
        user.englishLevel = 'A2'
    elif points <= 900:
        user.englishLevel = 'B1'
    elif points <= 1200:
        user.englishLevel = 'B2'
    elif points <= 1500:
        user.englishLevel = 'C1'
    else:
        user.englishLevel = 'C2'
            
    await db.commit()
    
    return user

# Rangos de puntos para cada nivel
CONST_LEVELS_RANGES = {
    'A1': (0, 300),
    'A2': (301, 600),
    'B1': (601, 900),
    'B2': (901, 1200),
    'C1': (1201, 1500),
    'C2': (1501, float('inf'))
}

async def get_answer_feedback(
    db: AsyncSession,
    response_id: int,
    question_id: int
) -> dict:
    """
    Obtiene el feedback detallado de una respuesta específica.
    Si la pregunta no tiene opciones, re-analiza la respuesta con IA.
    """
    try:
        # Obtener la respuesta del usuario
        result = await db.execute(
            select(UserAnswer)
            .where(
                UserAnswer.exercise_response_id == response_id,
                UserAnswer.question_id == question_id
            )
        )
        user_answer = result.scalar_one_or_none()
        
        if not user_answer:
            return None
        
        # Obtener la pregunta con sus opciones
        result = await db.execute(
            select(Question)
            .options(selectinload(Question.options))
            .where(Question.id == question_id)
        )
        question = result.scalar_one_or_none()
        
        if not question:
            return None
        
        # Si la pregunta no tiene opciones y hay texto de respuesta, re-analizar con IA
        if not question.options and user_answer.answer_text:
            logger.info("Re-analyzing text response with AI for detailed feedback")
            ai_analysis = await analyze_text_response(
                question_text=question.question_text,
                correct_answer=question.correct_answer,
                user_answer=user_answer.answer_text,
                explanation=question.explanation
            )
            
            return {
                "question_id": question.id,
                "question_text": question.question_text,
                "user_answer": user_answer.answer_text,
                "correct_answer": question.correct_answer,
                "is_correct": ai_analysis["is_correct"],
                "score_percentage": ai_analysis["score_percentage"],
                "feedback": ai_analysis["feedback"],
                "points_earned": int((ai_analysis["score_percentage"] / 100) * question.points),
                "total_points": question.points
            }
        else:
            # Para preguntas con opciones o sin texto de respuesta, devolver información básica
            return {
                "question_id": question.id,
                "question_text": question.question_text,
                "user_answer": user_answer.answer_text or "Opción seleccionada",
                "correct_answer": question.correct_answer,
                "is_correct": user_answer.is_correct,
                "score_percentage": 100 if user_answer.is_correct else 0,
                "feedback": "Respuesta evaluada automáticamente",
                "points_earned": user_answer.points_earned,
                "total_points": question.points
            }
            
    except Exception as e:
        logger.error(f"Error getting answer feedback: {str(e)}")
        return None