from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.content_service import get_content, create_content, assign_users_to_content, get_content_with_users, get_all_content_with_users
from app.schemas.content import ContentCreate, ContentUserAssignment, ContentWithUsers

router = APIRouter()

@router.get("/")
async def get_content_endpoint(db: AsyncSession = Depends(get_db)):
    content = await get_content(db)
    return content

@router.post("/create")
async def create_content_endpoint(content: ContentCreate, db: AsyncSession = Depends(get_db)):
    try:
        created_content = await create_content(db, content)
        return {
            "message": "Content created successfully",
            "content": {
                "id": created_content.id,
                "thematic": created_content.thematic,
                "link": created_content.link,
                "title": created_content.title,
                "img": created_content.img
            },
            "users_assigned": len(content.user_ids) if content.user_ids else 0
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/assign-users")
async def assign_users_to_content_endpoint(assignment: ContentUserAssignment, db: AsyncSession = Depends(get_db)):
    try:
        content = await assign_users_to_content(db, assignment)
        return {"message": "Users assigned successfully", "content_id": content.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/with-users")
async def get_all_content_with_users_endpoint(db: AsyncSession = Depends(get_db)):
    content = await get_all_content_with_users(db)
    return content

@router.get("/{content_id}/with-users")
async def get_content_with_users_endpoint(content_id: int, db: AsyncSession = Depends(get_db)):
    content = await get_content_with_users(db, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content