import firebase_admin
from firebase_admin import credentials, storage
import os
from typing import Optional

class FirebaseConfig:
    def __init__(self):
        self.bucket = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Inicializar Firebase Admin SDK"""
        try:
            # Verificar si las variables de entorno están configuradas
            firebase_bucket = os.getenv('FIREBASE_STORAGE_BUCKET')
            credentials_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            
            if not firebase_bucket:
                print("⚠️  Firebase Storage no configurado. Las funciones de archivos no estarán disponibles.")
                print("   Configura FIREBASE_STORAGE_BUCKET en tu archivo .env")
                return
            
            # Limpiar el formato del bucket (remover gs:// si está presente)
            if firebase_bucket.startswith('gs://'):
                firebase_bucket = firebase_bucket[5:]  # Remover 'gs://'
            
            print(f"🔧 Usando bucket: {firebase_bucket}")
            
            # Opción 1: Usar archivo de credenciales (recomendado para producción)
            if credentials_file and os.path.exists(credentials_file):
                cred = credentials.Certificate(credentials_file)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': firebase_bucket
                })
                print("✅ Firebase Storage inicializado con archivo de credenciales")
            else:
                # Opción 2: Usar variables de entorno (para desarrollo)
                firebase_admin.initialize_app({
                    'storageBucket': firebase_bucket
                })
                print("✅ Firebase Storage inicializado con variables de entorno")
            
            self.bucket = storage.bucket()
            
        except Exception as e:
            print(f"❌ Error inicializando Firebase: {e}")
            print("   Las funciones de archivos no estarán disponibles")
            self.bucket = None
    
    def get_bucket(self):
        """Obtener el bucket de Storage"""
        return self.bucket
    
    def is_configured(self):
        """Verificar si Firebase está configurado"""
        return self.bucket is not None

# Instancia global
firebase_config = FirebaseConfig() 