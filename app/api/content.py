from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.services.content_service import get_content, create_content, assign_users_to_content, get_content_with_users, get_all_content_with_users, check_link_exists, generate_unique_link, get_content_by_user_id
from app.services.file_service import file_service
from app.schemas.content import ContentCreate, ContentUserAssignment, ContentWithUsers
from app.core.firebase_config import firebase_config
from typing import Optional
import base64
import os

router = APIRouter()

@router.get("/firebase-status")
async def firebase_status_endpoint():
    """Endpoint para diagnosticar el estado de Firebase"""
    status = {
        "firebase_configured": firebase_config.is_configured(),
        "bucket_available": firebase_config.get_bucket() is not None,
        "environment_vars": {
            "FIREBASE_STORAGE_BUCKET": os.getenv('FIREBASE_STORAGE_BUCKET'),
            "GOOGLE_APPLICATION_CREDENTIALS": os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            "credentials_file_exists": os.path.exists(os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')) if os.getenv('GOOGLE_APPLICATION_CREDENTIALS') else False
        }
    }
    
    if firebase_config.get_bucket():
        try:
            # Intentar una operación simple para verificar conectividad
            bucket_name = firebase_config.get_bucket().name
            status["bucket_name"] = bucket_name
            status["connection_test"] = "✅ Conectado"
        except Exception as e:
            status["connection_test"] = f"❌ Error: {str(e)}"
    else:
        status["connection_test"] = "❌ No configurado"
    
    return status

@router.get("/")
async def get_content_endpoint(db: AsyncSession = Depends(get_db)):
    content = await get_content(db)
    return content

@router.post("/create")
async def create_content_endpoint(
    thematic: str = Form(...),
    link: str = Form(...),
    title: str = Form(...),
    image_file: Optional[UploadFile] = File(None),  # Ahora es opcional
    image_url: Optional[str] = Form(None),  # Nueva opción para URL externa
    user_ids: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    try:
        print(f"📝 Recibiendo datos: thematic={thematic}, link={link}, title={title}")
        print(f"   image_file: {image_file.filename if image_file else 'None'}")
        print(f"   image_url: {image_url}")
        print(f"   user_ids: {user_ids}")
        
        image_url_final = None
        
        # Opción 1: Subir imagen a Firebase Storage
        if image_file:
            print(f"🖼️  Intentando subir imagen: {image_file.filename}")
            print(f"   Tipo: {image_file.content_type}")
            print(f"   Tamaño: {image_file.size if hasattr(image_file, 'size') else 'desconocido'}")
            
            try:
                image_url_final = await file_service.save_image(image_file)
                print(f"✅ Imagen subida exitosamente: {image_url_final}")
            except Exception as e:
                print(f"❌ Error subiendo a Firebase: {str(e)}")
                print(f"   Tipo de error: {type(e).__name__}")
                # Si Firebase falla, usar URL por defecto
                image_url_final = "https://via.placeholder.com/400x300?text=Error+Firebase"
        
        # Opción 2: Usar URL externa proporcionada
        elif image_url:
            print(f"🔗 Usando URL externa: {image_url}")
            image_url_final = image_url
        
        # Opción 3: URL por defecto si no hay imagen
        else:
            print("📷 No se proporcionó imagen, usando placeholder")
            image_url_final = "https://via.placeholder.com/400x300?text=Sin+imagen"
        
        print(f"🎯 URL final de imagen: {image_url_final}")
        
        # Crear objeto de contenido
        content_data = ContentCreate(
            thematic=thematic,
            link=link,
            title=title,
            img=image_url_final,
            user_ids=user_ids.split(',') if user_ids else []
        )
        
        print(f"📦 Creando contenido con datos: {content_data}")
        
        created_content = await create_content(db, content_data)
        print(f"✅ Contenido creado con ID: {created_content.id}")
        
        return {
            "message": "Content created successfully",
            "content": {
                "id": created_content.id,
                "thematic": created_content.thematic,
                "link": created_content.link,
                "title": created_content.title,
                "img": created_content.img
            },
            "users_assigned": len(content_data.user_ids) if content_data.user_ids else 0
        }
    except HTTPException as e:
        # Re-raise HTTPExceptions (como el error de link duplicado)
        raise e
    except Exception as e:
        print(f"💥 Error en create_content_endpoint: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

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

@router.put("/{content_id}/update-image")
async def update_content_image_endpoint(
    content_id: int,
    image_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Obtener contenido actual
        content = await get_content_with_users(db, content_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Actualizar imagen
        new_image_url = await file_service.update_file(
            content.img, 
            image_file, 
            "image"
        )
        
        # Actualizar en base de datos
        from app.models.content import Content
        content_result = await db.execute(
            select(Content).where(Content.id == content_id)
        )
        db_content = content_result.scalar_one_or_none()
        if db_content:
            db_content.img = new_image_url
            await db.commit()
        
        return {
            "message": "Image updated successfully",
            "img": new_image_url
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/create-auto-link")
async def create_content_auto_link_endpoint(
    thematic: str = Form(...),
    link: str = Form(...),
    title: str = Form(...),
    image_file: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None),
    user_ids: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Endpoint que genera automáticamente un link único si el proporcionado ya existe"""
    try:
        print(f"📝 Recibiendo datos: thematic={thematic}, link={link}, title={title}")
        
        # Generar link único automáticamente
        unique_link = await generate_unique_link(db, link)
        if unique_link != link:
            print(f"🔄 Link modificado de '{link}' a '{unique_link}' para evitar duplicados")
        
        image_url_final = None
        
        # Opción 1: Subir imagen a Firebase Storage
        if image_file:
            print(f"🖼️  Intentando subir imagen: {image_file.filename}")
            try:
                image_url_final = await file_service.save_image(image_file)
                print(f"✅ Imagen subida exitosamente: {image_url_final}")
            except Exception as e:
                print(f"❌ Error subiendo a Firebase: {str(e)}")
                image_url_final = "https://via.placeholder.com/400x300?text=Error+Firebase"
        
        # Opción 2: Usar URL externa proporcionada
        elif image_url:
            print(f"🔗 Usando URL externa: {image_url}")
            image_url_final = image_url
        
        # Opción 3: URL por defecto si no hay imagen
        else:
            print("📷 No se proporcionó imagen, usando placeholder")
            image_url_final = "https://via.placeholder.com/400x300?text=Sin+imagen"
        
        # Crear objeto de contenido con el link único
        content_data = ContentCreate(
            thematic=thematic,
            link=unique_link,
            title=title,
            img=image_url_final,
            user_ids=user_ids.split(',') if user_ids else []
        )
        
        print(f"📦 Creando contenido con datos: {content_data}")
        
        created_content = await create_content(db, content_data)
        print(f"✅ Contenido creado con ID: {created_content.id}")
        
        return {
            "message": "Content created successfully",
            "content": {
                "id": created_content.id,
                "thematic": created_content.thematic,
                "link": created_content.link,
                "title": created_content.title,
                "img": created_content.img
            },
            "users_assigned": len(content_data.user_ids) if content_data.user_ids else 0,
            "link_modified": unique_link != link,
            "original_link": link if unique_link != link else None
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"💥 Error en create_content_auto_link_endpoint: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/check-link/{link}")
async def check_link_exists_endpoint(link: str, db: AsyncSession = Depends(get_db)):
    """Endpoint para verificar si un link ya existe"""
    exists = await check_link_exists(db, link)
    return {
        "link": link,
        "exists": exists,
        "message": "Link ya existe" if exists else "Link disponible"
    }

@router.get("/getbyuser/{user_id}")
async def get_content_by_user_id_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    from app.services.content_service import get_content_by_user_id
    content = await get_content_by_user_id(db, user_id)
    return content