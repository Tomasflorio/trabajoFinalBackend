from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings
from pathlib import Path
import secrets
import string
from datetime import datetime, timedelta

class EmailService:
    def __init__(self):
        # Solo inicializar si las credenciales de email están configuradas
        if settings.MAIL_USERNAME and settings.MAIL_PASSWORD and settings.MAIL_FROM:
            self.conf = ConnectionConfig(
                MAIL_USERNAME=settings.MAIL_USERNAME,
                MAIL_PASSWORD=settings.MAIL_PASSWORD,
                MAIL_FROM=settings.MAIL_FROM,
                MAIL_PORT=settings.MAIL_PORT,
                MAIL_SERVER=settings.MAIL_SERVER,
                MAIL_STARTTLS=True,
                MAIL_SSL_TLS=False,
                USE_CREDENTIALS=True,
                TEMPLATE_FOLDER=None  # No usar templates por ahora
            )
            self.fastmail = FastMail(self.conf)
            self.email_configured = True
        else:
            self.email_configured = False
            print("⚠️  Email no configurado. Las funciones de recupero de contraseña no funcionarán.")
    
    def generate_reset_token(self) -> str:
        """Genera un token seguro para el recupero de contraseña"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(8))  # Token más corto para facilitar ingreso
    
    def get_token_expiration(self) -> datetime:
        """Obtiene la fecha de expiración del token"""
        return datetime.utcnow() + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
    
    async def send_password_reset_email(self, email: str, token: str, user_name: str):
        """Envía el email de recupero de contraseña con el token"""
        if not self.email_configured:
            raise Exception("Email no configurado. Configura las variables de entorno de email.")
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; text-align: center;">
                <h2 style="color: #333; margin-bottom: 20px;">🔐 Recupero de Contraseña</h2>
                
                <p style="color: #666; font-size: 16px; margin-bottom: 20px;">
                    Hola <strong>{user_name}</strong>,
                </p>
                
                <p style="color: #666; font-size: 16px; margin-bottom: 30px;">
                    Has solicitado recuperar tu contraseña. Usa el siguiente código para restablecer tu contraseña:
                </p>
                
                <div style="background-color: #007bff; color: white; padding: 20px; border-radius: 8px; margin: 30px 0;">
                    <h1 style="margin: 0; font-size: 32px; letter-spacing: 5px; font-family: 'Courier New', monospace;">
                        {token}
                    </h1>
                </div>
                
                <p style="color: #666; font-size: 14px; margin-bottom: 20px;">
                    ⏰ Este código expirará en <strong>{settings.RESET_TOKEN_EXPIRE_MINUTES} minutos</strong>.
                </p>
                
                <p style="color: #666; font-size: 14px; margin-bottom: 20px;">
                    🚨 Si no solicitaste este cambio, puedes ignorar este email.
                </p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                
                <p style="color: #999; font-size: 12px;">
                    Saludos,<br>
                    <strong>Tu equipo de soporte</strong>
                </p>
            </div>
        </body>
        </html>
        """
        
        message = MessageSchema(
            subject="🔐 Código de Recupero de Contraseña",
            recipients=[email],
            body=html_content,
            subtype="html"
        )
        
        await self.fastmail.send_message(message)

email_service = EmailService() 