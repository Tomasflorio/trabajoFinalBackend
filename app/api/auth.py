from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession  # Importamos AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import create_user, authenticate_user, delete_user_router, update_user_router, request_password_reset, reset_password_with_token, validate_reset_token
from app.schemas.user import LoginRequest, UserCreate, RegisterResponse, ForgotPasswordRequest, ResetPasswordRequest, PasswordResetResponse, ValidateTokenRequest
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
        "isAdmin": new_user.isAdmin,
        "englishLevel": new_user.englishLevel
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
        "isAdmin": user.isAdmin,
        "englishLevel": user.englishLevel
    }
    return {"message": "Login successful", "user": user_response, "status": 200}

@router.post("/forgot-password", response_model=PasswordResetResponse)
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Solicita el recupero de contraseña enviando un email con token"""
    success, message = await request_password_reset(db, request.email)
    
    if success:
        return {"message": message, "status": 200}
    else:
        raise HTTPException(status_code=400, detail=message)

@router.post("/validate-token", response_model=PasswordResetResponse)
async def validate_token(request: ValidateTokenRequest, db: AsyncSession = Depends(get_db)):
    """Valida el token de recupero de contraseña"""
    success, message = await validate_reset_token(db, request.token)
    
    if success:
        return {"message": message, "status": 200}
    else:
        raise HTTPException(status_code=400, detail=message)

@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Resetea la contraseña usando el token proporcionado"""
    success, message = await reset_password_with_token(db, request.token, request.new_password)
    
    if success:
        return {"message": message, "status": 200}
    else:
        raise HTTPException(status_code=400, detail=message)
