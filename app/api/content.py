from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.content_service import get_content, create_content
from app.schemas.content import ContentCreate

router = APIRouter()

@router.get("/")
async def get_content_endpoint(db: AsyncSession = Depends(get_db)):
    content = await get_content(db)
    return content

@router.post("/create")
async def create_content_endpoint(content: ContentCreate, db: AsyncSession = Depends(get_db)):
    content = await create_content(db, content)
    return content