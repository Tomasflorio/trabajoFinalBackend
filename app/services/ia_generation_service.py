from openai import OpenAI
import os
import json

def generatePrompt(exercise_type, english_level, title, userRequest, valid=False):
    
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
        prompt = generatePrompt(exercise_type,english_level,title,userRequested)
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
