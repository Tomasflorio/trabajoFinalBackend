from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.exercise import DifficultyLevel  # Importa el Enum

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    correct_answer = Column(String(255))
    explanation = Column(Text)
    order = Column(Integer, default=0)
    points = Column(Integer, nullable=False, default=1)  # Nuevo campo
    difficulty = Column(Enum(DifficultyLevel), nullable=False, default="easy")  # Nuevo campo

    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")
    exercise = relationship("Exercise", back_populates="questions")
