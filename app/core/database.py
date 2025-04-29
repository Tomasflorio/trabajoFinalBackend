from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from dotenv import load_dotenv
import os

# Crear una clase base para la ORM de SQLAlchemy
Base = declarative_base()

# Definir la URL de la base de datos
load_dotenv()

# Obtener la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear el motor asíncrono
engine = create_async_engine(DATABASE_URL, echo=True)

# Crear un sessionmaker asíncrono correctamente nombrado
async_session_maker = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Función para obtener la sesión de la base de datos
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session