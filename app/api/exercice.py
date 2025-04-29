from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession  # Importamos AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.exercice_service import create_exercice_router
from app.schemas.exercice import ExerciceCreate, CreateExerciceResponse
from app.models.user import User

router = APIRouter()

@router.post("/create", response_model=CreateExerciceResponse)
async def create_exercice(exercice_data: ExerciceCreate, db: AsyncSession = Depends(get_db)):
    new_exercice = await create_exercice_router(db, exercice_data)

    exercice_response = {
        "id": new_exercice.id,
        "type": new_exercice.type,
        "response": new_exercice.response,
        "content": new_exercice.content,
        "valid": new_exercice.valid,
        "value": int(new_exercice.value),  # Asegúrate de convertir a int si es necesario
        "level": new_exercice.level
    }
    return {"message": "Ejercicio creado", "exercice": exercice_response, "status": 201}