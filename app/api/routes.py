from fastapi import APIRouter

from app.api import question
from app.api import user
from app.api import auth
from app.api import exercice

router = APIRouter()

# Endpoint básico para la ruta "/"
@router.get("/")
def root():
    return {"message": "hello world"}

router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(exercice.router, prefix="/exercice", tags=["Exercice"])
router.include_router(user.router, prefix="/user", tags=["User"])
router.include_router(question.router, prefix="/questions", tags=["Questions"])