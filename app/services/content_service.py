from app.schemas.content import ContentCreate, ContentRead
from app.models.content import Content
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def get_content(db: AsyncSession):
    result = await db.execute(select(Content))
    return result.scalars().all()

async def create_content(db: AsyncSession, content: ContentCreate):
    new_content = Content(**content.model_dump())
    db.add(new_content)
    await db.commit()