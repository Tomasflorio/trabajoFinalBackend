from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate 
from app.utils.security import hash_password, verify_password
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.services.email_service import email_service
from datetime import datetime

def isAdmin(email: str):
    return email.split('@')[1]=='caece.edu.com'

async def create_user(db: Session, user_data: UserCreate):
    hashed_password = hash_password(user_data.password)
    adminValue= isAdmin(user_data.email)
    
    new_user =  new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
        points=0,
        isAdmin=adminValue
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def authenticate_user(db: Session, email: str, password: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user or not verify_password(password, user.password):
        return None
    return user

async def delete_user_router(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    
    await db.delete(user)
    await db.commit()
    return user

async def update_user_router(db: AsyncSession, user_id: int, updates: dict):
    print('User ID:', user_id)
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        return None

    for key, value in updates.items():
        if (key == "password"):
            value = hash_password(value)
        setattr(user, key, value)
    
    await db.commit()
    await db.refresh(user)
    return user

async def get_all_students(db: AsyncSession):
    result = await db.execute(select(User).filter(User.isAdmin == False))
    students = result.scalars().all()
    return students

# Funciones para recupero de contraseña
async def request_password_reset(db: AsyncSession, email: str):
    """Solicita el recupero de contraseña enviando un email con token"""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if not user:
        return False, "Usuario no encontrado"
    
    # Verificar si el email está configurado
    if not email_service.email_configured:
        return False, "Sistema de email no configurado. Contacta al administrador."
    
    # Generar token y fecha de expiración
    reset_token = email_service.generate_reset_token()
    token_expires = email_service.get_token_expiration()
    
    # Actualizar usuario con el token
    user.reset_token = reset_token
    user.reset_token_expires = token_expires
    
    await db.commit()
    
    # Enviar email
    try:
        await email_service.send_password_reset_email(email, reset_token, user.name)
        return True, "Email de recupero enviado exitosamente"
    except Exception as e:
        # Si falla el envío, limpiar el token
        user.reset_token = None
        user.reset_token_expires = None
        await db.commit()
        return False, f"Error al enviar email: {str(e)}"

async def validate_reset_token(db: AsyncSession, token: str):
    """Valida el token de recupero de contraseña sin resetearlo"""
    result = await db.execute(
        select(User).where(
            User.reset_token == token,
            User.reset_token_expires > datetime.utcnow()
        )
    )
    user = result.scalars().first()
    
    if not user:
        return False, "Token inválido o expirado"
    
    return True, "Token válido"

async def reset_password_with_token(db: AsyncSession, token: str, new_password: str):
    """Resetea la contraseña usando el token proporcionado"""
    result = await db.execute(
        select(User).where(
            User.reset_token == token,
            User.reset_token_expires > datetime.utcnow()
        )
    )
    user = result.scalars().first()
    
    if not user:
        return False, "Token inválido o expirado"
    
    # Actualizar contraseña y limpiar token
    user.password = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    
    await db.commit()
    
    return True, "Contraseña actualizada exitosamente"
