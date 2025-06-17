from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.user_service import delete_user_router, update_user_router, get_all_students
from typing import List
from app.models.user import User

router = APIRouter()

@router.get("/students", response_model=List[dict])
async def get_students(db: AsyncSession = Depends(get_db)):
    students = await get_all_students(db)
    return [{
        "id": student.id, 
        "name": student.name, 
        "email": student.email, 
        "points": student.points,
        "englishLevel": student.englishLevel.value if student.englishLevel else None
    } for student in students]

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await delete_user_router(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted", "status": 200}

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None
    

@router.put("/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    print("User ID:", user_id)
    updates = user_data.model_dump(exclude_unset=True)
    user = await update_user_router(db, user_id, updates)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated", "user": user, "status": 200}