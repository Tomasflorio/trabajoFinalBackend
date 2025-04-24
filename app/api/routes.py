from fastapi import APIRouter

from app.api import auth

router = APIRouter()

# Endpoint básico para la ruta "/"
@router.get("/")
def root():
    return {"message": "hello world"}

router.include_router(auth.router, prefix="/auth", tags=["Auth"])