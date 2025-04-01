from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Crear una clase base para la ORM de SQLAlchemy
Base = declarative_base()

# Definir la URL de la base de datos
DATABASE_URL = "mysql+aiomysql://root:@localhost/trabajofinaldb"

# Crear el motor asíncrono
engine = create_async_engine(DATABASE_URL, echo=True)

# Crear una sesión asíncrona
AsyncSession = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
