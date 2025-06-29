#!/usr/bin/env python3
"""
Script de prueba para verificar la subida de imágenes
"""

import requests
import os
from pathlib import Path

def test_firebase_status():
    """Probar el endpoint de estado de Firebase"""
    print("🔍 Verificando estado de Firebase...")
    response = requests.get("http://localhost:8000/content/firebase-status")
    if response.status_code == 200:
        status = response.json()
        print("✅ Firebase Status:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        return status
    else:
        print(f"❌ Error: {response.status_code}")
        return None

def test_image_upload():
    """Probar la subida de imagen"""
    print("\n🖼️  Probando subida de imagen...")
    
    # Crear una imagen de prueba simple
    test_image_path = "test_image.png"
    
    # Crear una imagen PNG simple de 1x1 pixel
    png_data = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 image
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,  # Color type, compression, filter, interlace
        0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk
        0x54, 0x08, 0x99, 0x01, 0x01, 0x00, 0x00, 0xFF,  # Image data
        0xFF, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0xE2,  # End of IDAT
        0x21, 0xBC, 0x33, 0x00, 0x00, 0x00, 0x00, 0x49,  # IEND chunk
        0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
    ])
    
    with open(test_image_path, 'wb') as f:
        f.write(png_data)
    
    try:
        # Probar subida de imagen
        with open(test_image_path, 'rb') as f:
            files = {'image_file': ('test.png', f, 'image/png')}
            data = {
                'thematic': 'technology',
                'link': 'https://test.com',
                'title': 'Test Image Upload'
            }
            
            response = requests.post(
                "http://localhost:8000/content/create",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Imagen subida exitosamente!")
            print(f"   ID: {result['content']['id']}")
            print(f"   Imagen URL: {result['content']['img']}")
            
            # Verificar que la imagen es accesible
            img_response = requests.get(result['content']['img'])
            if img_response.status_code == 200:
                print("✅ Imagen accesible desde la URL")
            else:
                print(f"⚠️  Imagen no accesible: {img_response.status_code}")
                
        else:
            print(f"❌ Error en subida: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    finally:
        # Limpiar archivo de prueba
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

def test_url_upload():
    """Probar subida con URL externa"""
    print("\n🔗 Probando subida con URL externa...")
    
    data = {
        'thematic': 'science',
        'link': 'https://test.com',
        'title': 'Test URL Upload',
        'image_url': 'https://via.placeholder.com/400x300?text=Test'
    }
    
    response = requests.post(
        "http://localhost:8000/content/create",
        data=data
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Contenido creado con URL externa!")
        print(f"   ID: {result['content']['id']}")
        print(f"   Imagen URL: {result['content']['img']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   Respuesta: {response.text}")

if __name__ == "__main__":
    print("🧪 Iniciando pruebas de subida de imágenes...")
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get("http://localhost:8000/")
        print("✅ Servidor está corriendo")
    except requests.exceptions.ConnectionError:
        print("❌ Servidor no está corriendo. Ejecuta: uvicorn app.main:app --reload")
        exit(1)
    
    # Ejecutar pruebas
    test_firebase_status()
    test_image_upload()
    test_url_upload()
    
    print("\n🎉 Pruebas completadas!") 