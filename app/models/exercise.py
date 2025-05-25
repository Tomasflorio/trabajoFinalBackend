from sqlalchemy import Column, Integer, String, Enum, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
import enum

class ExerciseType(enum.Enum):
    listening = "listening"
    reading = "reading"
    grammar = "grammar"
    writing = "writing"

class EnglishLevel(enum.Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

class DifficultyLevel(enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(ExerciseType), nullable=False)
    level = Column(Enum(EnglishLevel), nullable=False)
    valid = Column(Boolean, default=False)
    instructions = Column(Text, nullable=False)
    content_text = Column(Text)
    content_audio_url = Column(Text)

    questions = relationship("Question", back_populates="exercise", cascade="all, delete-orphan")
