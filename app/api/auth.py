from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession  # Importamos AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import create_user, authenticate_user
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