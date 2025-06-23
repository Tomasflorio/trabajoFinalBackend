from app.schemas.content import ContentCreate, ContentRead, ContentUserAssignment, ContentWithUsers
from app.models.content import Content
from app.models.user import User
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

async def get_content(db: AsyncSession):
    result = await db.execute(select(Content))
    return result.scalars().all()

async def create_content(db: AsyncSession, content: ContentCreate):
    user_ids = content.user_ids
    content_data = content.model_dump(exclude={'user_ids'})
    new_content = Content(**content_data)
    db.add(new_content)
    await db.commit()
    await db.refresh(new_content)

    # Asignar usuarios manualmente en la tabla intermedia
    if user_ids:
        for user_id in user_ids:
            await db.execute(
                text("INSERT INTO content_user_assignment (content_id, user_id) VALUES (:content_id, :user_id)"),
                {"content_id": new_content.id, "user_id": user_id}
            )
        await db.commit()
    return new_content

async def assign_users_to_content(db: AsyncSession, assignment: ContentUserAssignment):
    # Verificar que el contenido existe
    content_result = await db.execute(select(Content).where(Content.id == assignment.content_id))
    content = content_result.scalar_one_or_none()
    if not content:
        raise ValueError(f"Content with id {assignment.content_id} not found")
    # Verificar que los usuarios existen
    users_result = await db.execute(select(User).where(User.id.in_(assignment.user_ids)))
    users = users_result.scalars().all()
    if len(users) != len(assignment.user_ids):
        raise ValueError("Some users not found")
    # Eliminar asignaciones previas
    await db.execute(
        text("DELETE FROM content_user_assignment WHERE content_id = :content_id"),
        {"content_id": assignment.content_id}
    )
    # Insertar nuevas asignaciones
    for user_id in assignment.user_ids:
        await db.execute(
            text("INSERT INTO content_user_assignment (content_id, user_id) VALUES (:content_id, :user_id)"),
            {"content_id": assignment.content_id, "user_id": user_id}
        )
    await db.commit()
    return content

async def get_content_with_users(db: AsyncSession, content_id: int):
    result = await db.execute(select(Content).where(Content.id == content_id))
    content = result.scalar_one_or_none()
    if not content:
        return None
    # Obtener los IDs de usuarios asignados con SQL puro
    user_ids_result = await db.execute(
        text("SELECT user_id FROM content_user_assignment WHERE content_id = :content_id"),
        {"content_id": content_id}
    )
    user_ids = [row[0] for row in user_ids_result.fetchall()]
    return ContentWithUsers(
        id=content.id,
        thematic=content.thematic,
        link=content.link,
        title=content.title,
        img=content.img,
        assigned_users=user_ids
    )

async def get_all_content_with_users(db: AsyncSession):
    result = await db.execute(select(Content))
    contents = result.scalars().all()
    content_with_users = []
    for content in contents:
        user_ids_result = await db.execute(
            text("SELECT user_id FROM content_user_assignment WHERE content_id = :content_id"),
            {"content_id": content.id}
        )
        user_ids = [row[0] for row in user_ids_result.fetchall()]
        content_with_users.append(ContentWithUsers(
            id=content.id,
            thematic=content.thematic,
            link=content.link,
            title=content.title,
            img=content.img,
            assigned_users=user_ids
        ))
    return content_with_users