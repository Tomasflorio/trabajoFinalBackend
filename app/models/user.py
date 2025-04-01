from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean,  Enum as SQLEnum
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class EnglishLevel(Enum):
    A1 = 'A1'
    A2 = 'A2'
    B1 = 'B1'
    B2 = 'B2'
    C1 = 'C1'
    C2 = 'C2'

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    points = Column(Integer, default=0)
    isAdmin = Column(Boolean, nullable=False)
    englishLevel = Column(SQLEnum(EnglishLevel, name="english_level"), nullable=False)