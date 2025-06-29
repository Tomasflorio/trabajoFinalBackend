from fastapi import APIRouter

from app.api import question
from app.api import user
from app.api import auth
from app.api import exercise
from app.api import exercise_response
from app.api import iaGenerartion
from app.api import content

router = APIRouter()

# Endpoint básico para la ruta "/"
@router.get("/")
def root():
    return {"message": "hello world"}

router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(exercise.router, prefix="/exercise", tags=["Exercise"])  # Cambia el prefijo si renombras
router.include_router(user.router, prefix="/user", tags=["User"])
router.include_router(question.router, prefix="/questions", tags=["Questions"])
router.include_router(exercise_response.router, prefix="/exercise", tags=["Exercise Responses"])
router.include_router(iaGenerartion.router, prefix="/ia", tags=["iaGeneration"])
router.include_router(content.router, prefix="/content", tags=["Content"])