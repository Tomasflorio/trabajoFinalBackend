import os
import uuid
from fastapi import UploadFile, HTTPException
from PIL import Image
import io
from typing import Optional
from google.cloud import storage
from app.core.firebase_config import firebase_config

class FirebaseFileService:
    def __init__(self):
        self.bucket = firebase_config.get_bucket()
        self.allowed_image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        self.allowed_audio_types = ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg', 'audio/m4a']
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        
        # Crear directorio para imágenes locales si no existe
        self.local_images_dir = "static/images"
        os.makedirs(self.local_images_dir, exist_ok=True)
    
    def _check_firebase_configured(self):
        """Verificar si Firebase está configurado"""
        if not firebase_config.is_configured():
            raise HTTPException(
                status_code=503,
                detail="Firebase Storage no está configurado. Contacta al administrador."
            )
    
    async def save_image_locally(self, file: UploadFile) -> str:
        """Guardar imagen localmente como fallback"""
        try:
            # Validar tipo de archivo
            if not file.content_type in self.allowed_image_types:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Tipo de imagen no soportado. Tipos permitidos: {', '.join(self.allowed_image_types)}"
                )
            
            # Leer contenido
            content = await file.read()
            if len(content) > self.max_file_size:
                raise HTTPException(status_code=400, detail="Archivo demasiado grande. Máximo 50MB")
            
            # Validar que sea una imagen válida
            try:
                image = Image.open(io.BytesIO(content))
                image.verify()
            except Exception:
                raise HTTPException(status_code=400, detail="Archivo de imagen inválido")
            
            # Generar nombre único
            file_extension = file.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(self.local_images_dir, unique_filename)
            
            # Guardar archivo localmente
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Retornar URL relativa
            return f"/static/images/{unique_filename}"
            
        except Exception as e:
            print(f"Error guardando imagen localmente: {e}")
            raise
    
    async def save_image(self, file: UploadFile) -> str:
        """Guardar imagen en Firebase Storage y retornar URL pública"""
        try:
            # Leer el contenido una sola vez
            content = await file.read()
            
            # Validar tipo de archivo
            if not file.content_type in self.allowed_image_types:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Tipo de imagen no soportado. Tipos permitidos: {', '.join(self.allowed_image_types)}"
                )
            
            # Validar tamaño
            if len(content) > self.max_file_size:
                raise HTTPException(status_code=400, detail="Archivo demasiado grande. Máximo 50MB")
            
            # Validar que sea una imagen válida
            try:
                image = Image.open(io.BytesIO(content))
                image.verify()
                # Resetear el archivo para que se pueda leer de nuevo
                await file.seek(0)
            except Exception as e:
                print(f"Error validando imagen: {e}")
                raise HTTPException(status_code=400, detail="Archivo de imagen inválido")
            
            # Intentar subir a Firebase primero
            if firebase_config.is_configured():
                try:
                    # Generar nombre único
                    file_extension = file.filename.split('.')[-1]
                    unique_filename = f"images/{uuid.uuid4()}.{file_extension}"
                    
                    # Subir a Firebase Storage
                    blob = self.bucket.blob(unique_filename)
                    blob.upload_from_string(content, content_type=file.content_type)
                    
                    # Hacer público el archivo
                    blob.make_public()
                    
                    print(f"✅ Imagen subida exitosamente a Firebase: {blob.public_url}")
                    return blob.public_url
                    
                except Exception as e:
                    print(f"❌ Error subiendo a Firebase: {e}")
                    print("Intentando guardar localmente...")
            
            # Fallback: guardar localmente
            return await self.save_image_locally_with_content(file, content)
            
        except HTTPException:
            # Re-lanzar HTTPExceptions
            raise
        except Exception as e:
            print(f"Error general guardando imagen: {e}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def save_image_locally_with_content(self, file: UploadFile, content: bytes) -> str:
        """Guardar imagen localmente usando contenido ya leído"""
        try:
            # Generar nombre único
            file_extension = file.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(self.local_images_dir, unique_filename)
            
            # Guardar archivo localmente
            with open(file_path, 'wb') as f:
                f.write(content)
            
            url_path = f"/static/images/{unique_filename}"
            print(f"✅ Imagen guardada localmente: {url_path}")
            return url_path
            
        except Exception as e:
            print(f"Error guardando imagen localmente: {e}")
            raise HTTPException(status_code=500, detail="Error guardando imagen localmente")
    
    async def save_audio(self, file: UploadFile) -> str:
        """Guardar archivo de audio en Firebase Storage y retornar URL pública"""
        self._check_firebase_configured()
        
        if not file.content_type in self.allowed_audio_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de audio no soportado. Tipos permitidos: {', '.join(self.allowed_audio_types)}"
            )
        
        # Validar tamaño
        content = await file.read()
        if len(content) > self.max_file_size:
            raise HTTPException(status_code=400, detail="Archivo demasiado grande. Máximo 50MB")
        
        # Generar nombre único
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"audio/{uuid.uuid4()}.{file_extension}"
        
        # Subir a Firebase Storage
        blob = self.bucket.blob(unique_filename)
        blob.upload_from_string(content, content_type=file.content_type)
        
        # Hacer público el archivo
        blob.make_public()
        
        return blob.public_url
    
    async def delete_file(self, file_url: str) -> bool:
        """Eliminar archivo de Firebase Storage"""
        if not firebase_config.is_configured():
            print("⚠️  Firebase no configurado, no se puede eliminar archivo")
            return False
            
        try:
            # Extraer el nombre del archivo de la URL
            # Ejemplo: https://storage.googleapis.com/bucket-name/images/filename.jpg
            file_path = file_url.split('/')[-2] + '/' + file_url.split('/')[-1]
            blob = self.bucket.blob(file_path)
            blob.delete()
            return True
        except Exception as e:
            print(f"Error eliminando archivo: {e}")
            return False
    
    async def update_file(self, old_url: str, new_file: UploadFile, file_type: str) -> str:
        """Actualizar archivo existente"""
        self._check_firebase_configured()
        
        # Eliminar archivo anterior
        if old_url:
            await self.delete_file(old_url)
        
        # Subir nuevo archivo
        if file_type == "image":
            return await self.save_image(new_file)
        elif file_type == "audio":
            return await self.save_audio(new_file)
        else:
            raise HTTPException(status_code=400, detail="Tipo de archivo no soportado")

# Instancia global
file_service = FirebaseFileService() 