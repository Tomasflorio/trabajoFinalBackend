from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import declarative_base
from app.models.user import EnglishLevel

Base = declarative_base()


class ExerciceType(Enum):
    LISTENING = "LISTENING"
    WRITING = "WRITING"
    READING_COMPREHENTION = "READING COMPREHENTION"
    GRAMMAR = "GRAMMAR"

class Exercice(Base):
    __tablename__ = "exercice"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(ExerciceType, name="exercice_type"), nullable=False)
    response = Column(String(255), unique=True, index=True, nullable=False)
    content = Column(String(255), nullable=False)
    valid = Column(Boolean, nullable=False)
    value = Column(String(255), default=0)
    level = Column(SQLEnum(EnglishLevel, name="english_level"), nullable=False)

    