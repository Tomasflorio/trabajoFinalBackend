from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from app.models.base import Base

class UserExerciseResponse(Base):
    __tablename__ = "user_exercise_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"))
    submitted_at = Column(DateTime(timezone=True), default=func.now())
    score = Column(Integer, default=0)
    is_valid = Column(Boolean, default=False)

    # Relaciones
    user = relationship("User", back_populates="exercise_responses")
    exercise = relationship("Exercise")
    answers = relationship("UserAnswer", back_populates="exercise_response", cascade="all, delete-orphan") 