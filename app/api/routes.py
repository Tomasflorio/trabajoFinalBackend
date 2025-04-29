from fastapi import APIRouter

from app.api import auth
from app.api import exercice

router = APIRouter()

# Endpoint básico para la ruta "/"
@router.get("/")
def root():
    return {"message": "hello world"}

router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(exercice.router, prefix="/exercice", tags=["Exercice"])