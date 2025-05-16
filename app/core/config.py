from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # Cargar variables desde el archivo .env


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    OPENAI_API_KEY: str  # <-- Agrega esta línea

    class Config:
        env_file = ".env"  # Indicar que debe leer desde .env

settings = Settings()