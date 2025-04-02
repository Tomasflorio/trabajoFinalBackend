from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate 
from app.utils.security import hash_password, verify_password
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

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