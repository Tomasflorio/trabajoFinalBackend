from fastapi import APIRouter

router = APIRouter()

# Endpoint básico para la ruta "/"
@router.get("/")
def root():
    return {"message": "hello world"}