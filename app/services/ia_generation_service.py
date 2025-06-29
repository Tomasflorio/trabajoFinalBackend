from openai import OpenAI
import os
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.exercise import Exercise
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

# Configurar el logger
logger = logging.getLogger(__name__)

def check_answer(user_answer: str, correct_answer: str) -> bool:
    """Verifica si la respuesta del usuario es correcta usando comparación básica."""
    if not user_answer or not correct_answer:
        return False
    
    # Convertir a minúsculas y eliminar espacios
    user_answer = user_answer.lower().strip()
    correct_answers = [ans.lower().strip() for ans in correct_answer.split('|')]
    
    # Verificar cada respuesta correcta
    for correct in correct_answers:
        if user_answer == correct:
            return True
    
    return False

def generateExercisePrompt(exercise_type, english_level, title, userRequest, valid=False):
    
    if (exercise_type != "listening"):
        prompt = f"""
    Quiero que generes un ejercicio educativo en ingles en el que alumno deba resolver preguntas que pueden ser de opcion multiple o de texto libre en formato JSON. 
    Debe seguir esta estructura:

    {{
    "title": "{title}",
    "type": "{exercise_type}",
    "level": "{english_level}",
    "valid": {str(valid).lower()},
    "instructions": "[Este campo debe contener las instrucciones claras para que un estudiante pueda resolver el ejercicio, por ejemplo: si las preguntas del campo question tienen opciones puede ser 'Selecciona la forma verbal correcta' si la pregunta es de completar con forma verbal o 'Rescribe correctamente la frase en el espacio provisto' si la pregunta es de texto libre y si se trata de rescribir una frase]", 
    "content_text": "[Este campo es opcional para el caso de que el ejercicio sea de grammar, writing o vocabulary, si es reading debe contener el texto a leer]",
    "content_audio_url": null
    "questions": "[Genera preguntas o consignas sobre el contenido del ejercicio, deben seguir la siguiente estructura:{{
        "question_text": "[texto de la pregunta o consigna]",
        "correct_answer": "[respuesta correcta]",
        "explanation": "[explicación de la respuesta correcta]",
        "order": [número de orden de la pregunta],
        "points": [puntos que se podrian asignar a la pregunta estos tienen que ser enteros, positivos y entre 50 y 100 teniendo en cuenta que entre 20 y 50 es es lo que se deberia valer a una pregunta de nivel facil, entre 50 y 75 una pregunta de nivel medio y entre 75 y 100 una pregunta de nivel dificil]",
        "difficulty": "[nivel de dificultad de la pregunta, puede ser easy, medium o hard]",
        "options": "[Esto es una lista de opciones de respuesta, si es una pregunta de opción múltiple en caso de que sea de texto libre dejalo vacio, debe seguir la siguiente estructura: {{"option_text": "[texto de la opción]", "is_correct": [booleano que indica si es la respuesta correcta]}}]"
        }}]"
    }}

    Quiero que generes un ejercicio de tipo: **{exercise_type}**, para este nivel de ingles: **{english_level}**, con instrucciones claras para un estudiante. 
    El texto a generar debe tener este propósito: **{userRequest}**, utiliza esto siempre para el title **{title}**.
    """
    else:
        pass

    return prompt

async def generateListeningExerciceAndAudio():
    return "Funcionalidad no implementada, por favor contacta al administrador del sistema para más información."


async def generate_exercise(exercise_type, english_level, title, userRequested):
    client = OpenAI( api_key=os.getenv("OPENAI_API_KEY"))
    if (exercise_type != "listening"):
        prompt = generateExercisePrompt(exercise_type,english_level,title,userRequested)
        response = client.chat.completions.create(
            model="gpt-4.1",  
            messages=[
                {"role": "system", "content": "Eres un generador de ejercicios educativos en JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7)
        output = response.choices[0].message.content.strip()
        exercise_json = json.loads(output)
        return exercise_json
    else:
        response = await generateListeningExerciceAndAudio()
        return response


def generateQuestionPrompt(exercise_type, english_level, userRequested, instructions, content_text, cantidad, tipoRespuesta, dificultad, preguntasExistentes):
    prompt = ""
    if (content_text != None):
        prompt = f"""
        Quiero que generes {cantidad} preguntas o consigas en ingles que tengan coherencia con estas instrucciones: {instructions} y el contenido del ejercicio: {content_text}, ademas el usuario solicita que las preguntas se formen siguiendo este mensaje: {userRequested}, el ejercicio es de tipo: {exercise_type} y nivel: {english_level} 
        estas pueden ser de {tipoRespuesta}, deben ser de una dificultad {dificultad} y deben ser en formato JSON. 
        No generes preguntas que ya existan en la siguiente lista: {preguntasExistentes}
        Siguiendo esta estructura:
        [
        {{
            "question_text": "[texto de la pregunta o consigna]",
            "correct_answer": "[respuesta correcta]",
            "explanation": "[explicación de la respuesta correcta]",
            "order": [número de orden de la pregunta],
            "points": [puntos que se podrian asignar a la pregunta estos tienen que ser enteros, positivos y entre 50 y 100 teniendo en cuenta que entre 20 y 50 es es lo que se deberia valer a una pregunta de nivel facil, entre 50 y 75 una pregunta de nivel medio y entre 75 y 100 una pregunta de nivel dificil]",
            "difficulty": "[nivel de dificultad de la pregunta, puede ser easy, medium o hard]",
            "options": "[Esto es una lista de opciones de respuesta, si es una pregunta de opción múltiple en caso de que sea de texto libre dejalo vacio, debe seguir la siguiente estructura: {{"option_text": "[texto de la opción]", "is_correct": [booleano que indica si es la respuesta correcta]}}]"
            }}]"
        ]
        """
    else:
        prompt = f"""
        Quiero que generes {cantidad} preguntas o consigas en ingles que tengan coherencia con estas instrucciones: {instructions}, ademas el usuario solicita que las preguntas se formen siguiendo este mensaje: {userRequested}, el ejercicio es de tipo: {exercise_type} y nivel: {english_level} 
        estas pueden ser de {tipoRespuesta}, deben ser de una dificultad {dificultad} y deben ser en formato JSON. 
        No generes preguntas que ya existan en la siguiente lista: {preguntasExistentes}
        Siguiendo esta estructura:
        [
        {{
            "question_text": "[texto de la pregunta o consigna]",
            "correct_answer": "[respuesta correcta]",
            "explanation": "[explicación de la respuesta correcta]",
            "order": [número de orden de la pregunta],
            "points": [puntos que se podrian asignar a la pregunta estos tienen que ser enteros, positivos y entre 50 y 100 teniendo en cuenta que entre 20 y 50 es es lo que se deberia valer a una pregunta de nivel facil, entre 50 y 75 una pregunta de nivel medio y entre 75 y 100 una pregunta de nivel dificil]",
            "difficulty": "[nivel de dificultad de la pregunta, puede ser easy, medium o hard]",
            "options": "[Esto es una lista de opciones de respuesta, si es una pregunta de opción múltiple en caso de que sea de texto libre dejalo vacio, debe seguir la siguiente estructura: {{"option_text": "[texto de la opción]", "is_correct": [booleano que indica si es la respuesta correcta]}}]"
            }}]"
        ]
        """
    
    return prompt


async def generate_question(cantidad, response_type, question_difficulty, userRequested, exercise_id, db: AsyncSession):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Obtener el ejercicio con sus preguntas usando selectinload
    stmt = select(Exercise).options(
        selectinload(Exercise.questions)
    ).where(Exercise.id == exercise_id)
    
    result = await db.execute(stmt)
    exercise = result.scalar_one_or_none()
    
    if not exercise:
        raise ValueError(f"Exercise with id {exercise_id} not found")
    
    exercise_type = exercise.type
    english_level = exercise.level
    instructions = exercise.instructions
    content_text = exercise.content_text
    existing_questions = exercise.questions

    if (exercise_type == "listening"):
        raise NotImplementedError("Listening exercises are not implemented yet")
        return None

    prompt = generateQuestionPrompt(exercise_type, english_level, userRequested, instructions, content_text, cantidad, response_type, question_difficulty, existing_questions)
    if (prompt == None):
        return None
    
    response = client.chat.completions.create(
        model="gpt-4.1",  
        messages=[
            {"role": "system", "content": "Eres un generador de ejercicios educativos en JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    output = response.choices[0].message.content.strip()
    question_json = json.loads(output)
    return question_json

async def analyze_text_response(
    question_text: str,
    correct_answer: str,
    user_answer: str,
    explanation: str = None
) -> dict:
    """
    Analiza una respuesta de texto libre usando IA para determinar si es correcta.
    
    Args:
        question_text: El texto de la pregunta
        correct_answer: La respuesta correcta esperada
        user_answer: La respuesta del usuario
        explanation: Explicación de la respuesta correcta (opcional)
    
    Returns:
        dict: Contiene 'is_correct' (bool), 'score_percentage' (int), y 'feedback' (str)
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""
    Eres un evaluador experto de ejercicios de inglés. Tu tarea es evaluar si la respuesta del estudiante es correcta.

    Pregunta: {question_text}
    Respuesta correcta esperada: {correct_answer}
    Respuesta del estudiante: {user_answer}
    {f"Explicación de la respuesta correcta: {explanation}" if explanation else ""}

    Evalúa la respuesta del estudiante considerando:
    1. Corrección gramatical
    2. Precisión semántica
    3. Coherencia con la pregunta
    4. Variaciones aceptables de la respuesta correcta
    5. Errores menores que no afectan la comprensión

    Responde en formato JSON con la siguiente estructura:
    {{
        "is_correct": true/false,
        "score_percentage": 0-100,
        "feedback": "Explicación detallada de por qué la respuesta es correcta o incorrecta, incluyendo sugerencias de mejora si es necesario"
    }}

    Sé justo pero riguroso. Si la respuesta es conceptualmente correcta pero tiene errores menores, considera darle una puntuación parcial.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un evaluador experto de ejercicios de inglés. Responde siempre en formato JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        output = response.choices[0].message.content.strip()
        result = json.loads(output)
        
        return {
            "is_correct": result.get("is_correct", False),
            "score_percentage": result.get("score_percentage", 0),
            "feedback": result.get("feedback", "No se pudo evaluar la respuesta")
        }
        
    except Exception as e:
        # En caso de error, usar evaluación básica como fallback
        logger.error(f"Error al analizar respuesta con IA: {str(e)}")
        return {
            "is_correct": check_answer(user_answer, correct_answer),
            "score_percentage": 100 if check_answer(user_answer, correct_answer) else 0,
            "feedback": "Evaluación automática debido a error en el análisis de IA"
        }