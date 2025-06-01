from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # Cargar variables desde el archivo .env


class Settings(BaseSettings):
    DATABASE_URL: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    OPENAI_API_KEY: str 

    class Config:
        env_file = ".env"  

settings = Settings()