from app.models.exercise import Exercise
from app.schemas.exercise import exerciseCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.question import Question
from app.models.option import Option
import logging

logger = logging.getLogger(__name__)

async def create_exercise_router(db: AsyncSession, data: exerciseCreate):
    new_ex = Exercise(**data.dict())
    db.add(new_ex)
    await db.commit()
    await db.refresh(new_ex)
    return new_ex

async def create_full_exercise_router(db: AsyncSession, data: exerciseCreate):
    try:
        # Crear el ejercicio base
        exercise_data = data.dict(exclude={'questions'})
        new_ex = Exercise(**exercise_data)
        db.add(new_ex)
        await db.flush()
        logger.info(f"Ejercicio base creado con ID: {new_ex.id}")

        # Crear las preguntas y sus opciones
        for question_data in data.questions:
            try:
                # Crear la pregunta
                question_dict = {
                    'exercise_id': new_ex.id,
                    'question_text': question_data.question_text,
                    'correct_answer': question_data.correct_answer,
                    'explanation': question_data.explanation,
                    'order': question_data.order,
                    'points': question_data.points,
                    'difficulty': question_data.difficulty
                }
                
                new_question = Question(**question_dict)
                db.add(new_question)
                await db.flush()
                logger.info(f"Pregunta creada con ID: {new_question.id}")

                # Crear las opciones
                for option_data in question_data.options:
                    try:
                        option_dict = {
                            'question_id': new_question.id,
                            'option_text': option_data.option_text,
                            'is_correct': option_data.is_correct
                        }
                        new_option = Option(**option_dict)
                        db.add(new_option)
                        logger.info(f"Opción creada para pregunta {new_question.id}")
                    except Exception as e:
                        logger.error(f"Error al crear opción: {str(e)}")
                        raise

            except Exception as e:
                logger.error(f"Error al crear pregunta: {str(e)}")
                raise

        await db.commit()
        logger.info("Commit realizado exitosamente")
        
        # Cargar el ejercicio con todas sus relaciones
        result = await db.execute(
            select(Exercise)
            .options(
                selectinload(Exercise.questions).selectinload(Question.options)
            )
            .filter_by(id=new_ex.id)
        )
        exercise = result.scalar_one()
        logger.info("Ejercicio cargado con relaciones")
        
        return exercise

    except Exception as e:
        logger.error(f"Error en create_full_exercise_router: {str(e)}")
        await db.rollback()
        raise

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
            options = []
            for option in question.options:
                options.append({
                    'option_text': option.option_text,
                    'is_correct': option.is_correct
                })
            formatted_questions.append({
                'id': question.id,
                'question_text': question.question_text,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation,
                'order': question.order,
                'points': question.points,
                'difficulty': question.difficulty,
                'options':  options  # Convertir objetos Option a strings
            })
        
        formatted_exercises.append({
            'id': exercise.id,
            'title': exercise.title,
            'type': exercise.type.value,
            'level': exercise.level.value,
            'valid': exercise.valid,
            'instructions': exercise.instructions,
            'content_text': exercise.content_text,
            'content_audio_url': exercise.content_audio_url,
            'questions': formatted_questions
        })
    
    return formatted_exercises

async def get_exercises_by_type_router(db: AsyncSession, exercise_type: str):
    result = await db.execute(
        select(Exercise)
        .options(selectinload(Exercise.questions).selectinload(Question.options))
        .filter_by(type=exercise_type)
    )
    exercises = result.scalars().all()
    
    # Convertir los ejercicios al formato esperado
    formatted_exercises = []
    for exercise in exercises:
        formatted_questions = []
        for question in exercise.questions:
            options = []
            for option in question.options:
                options.append({
                    'option_text': option.option_text,
                    'is_correct': option.is_correct
                })
            formatted_questions.append({
                'id': question.id,
                'question_text': question.question_text,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation,
                'order': question.order,
                'points': question.points,
                'difficulty': question.difficulty,
                'options': options  # Ahora devuelve toda la información de las opciones
            })
        
        formatted_exercises.append({
            'message': 'Ejercicio encontrado',
            'exercise': {
                'id': exercise.id,
                'title': exercise.title,
                'type': exercise.type.value,
                'level': exercise.level.value,
                'valid': exercise.valid,
                'instructions': exercise.instructions,
                'content_text': exercise.content_text,
                'content_audio_url': exercise.content_audio_url,
                'questions': formatted_questions
            },
            'status': 200
        })
    
    return formatted_exercises