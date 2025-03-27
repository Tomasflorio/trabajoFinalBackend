from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean
from app.db.session import Base 


class EnglishLevel(str, Enum):
    A1 = 'A1'
    A2 = 'A2'
    B1 = 'B1'
    B2 = 'B2'
    C1 = 'C1'
    C2 = 'C2'

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    points = Column(Integer, default=0)
    isAdmin = Column(Boolean, nullable=False)
    englishLevel = Column(EnglishLevel, nullable=False)