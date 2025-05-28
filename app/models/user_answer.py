from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.models.base import Base

class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    exercise_response_id = Column(Integer, ForeignKey("user_exercise_responses.id", ondelete="CASCADE"))
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))
    option_id = Column(Integer, ForeignKey("options.id", ondelete="SET NULL"), nullable=True)
    answer_text = Column(String(1000))
    is_correct = Column(Boolean, default=False)
    points_earned = Column(Integer, default=0)
    submitted_at = Column(DateTime(timezone=True), default=func.now())

    # Relaciones
    exercise_response = relationship("UserExerciseResponse", back_populates="answers")
    question = relationship("Question")
    option = relationship("Option") 