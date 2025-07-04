from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean,  Enum as SQLEnum, DateTime
from sqlalchemy.orm import declarative_base, relationship
from .base import Base
from datetime import datetime

class EnglishLevel(Enum):
    A1 = 'A1'
    A2 = 'A2'
    B1 = 'B1'
    B2 = 'B2'
    C1 = 'C1'
    C2 = 'C2'

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    points = Column(Integer, default=0)
    isAdmin = Column(Boolean, nullable=False)
    englishLevel = Column(SQLEnum(EnglishLevel, name="english_level"), nullable=True)
    
    # Campos para recupero de contraseña
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    # Relaciones
    exercise_responses = relationship("UserExerciseResponse", back_populates="user", cascade="all, delete-orphan")
    assigned_content = relationship("Content", secondary="content_user_assignment", back_populates="assigned_users")