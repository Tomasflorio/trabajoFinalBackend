from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession  # Importamos AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import create_user, authenticate_user, delete_user, update_user
from app.schemas.user import LoginRequest, UserCreate, RegisterResponse
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    print('solicitud registro')
    result = await db.execute(select(User).filter(User.email == user_data.email))
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = await create_user(db, user_data)  # Llamamos a `create_user` con `await`

    user_response = {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "isAdmin": new_user.isAdmin
    }

    return {"message": "Register successful", "user": user_response, "status": 201}

@router.post("/login")
async def login_user(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_response = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "isAdmin": user.isAdmin
    }
    return {"message": "Login successful", "user": user_response, "status": 200}

@router.delete("/user/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted", "status": 200}

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None
    

@router.put("/user/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    print("User ID:", user_id)
    updates = user_data.model_dump(exclude_unset=True)
    user = await update_user(db, user_id, updates)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated", "user": user, "status": 200}