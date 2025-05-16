from sqlalchemy.orm import Session
from app.schemas.exercice import ExerciceCreate 
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.exercice import Exercice


async def create_exercice_router(db: Session, exerciceData: ExerciceCreate):

    new_exercice = new_exercice = Exercice(
        type=exerciceData.type,
        response=exerciceData.response,
        content=exerciceData.content,
        valid=exerciceData.valid,
        value=exerciceData.value,
        level=exerciceData.level,
    )
    db.add(new_exercice)
    await db.commit()
    await db.refresh(new_exercice)
    return new_exercice

async def delete_exercice_router(db: AsyncSession, exercice_id: int):
    result = await db.execute(select(Exercice).filter(Exercice.id == exercice_id))
    exercice = result.scalar_one_or_none()
    
    if not exercice:
        return None
    
    await db.delete(exercice)
    await db.commit()
    return exercice

async def uptade_exercice_router(db: AsyncSession, exercice_id: int, updates: dict):
    result = await db.execute(select(Exercice).filter(Exercice.id == exercice_id))
    exercice = result.scalar_one_or_none()

    if not exercice:
        return None

    for key, value in updates.items():
        setattr(exercice, key, value)
    
    await db.commit()
    await db.refresh(exercice)
    return exercice