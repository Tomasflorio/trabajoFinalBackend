from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean
from app.db.session import Base


class ExerciceType(str, Enum):
    LISTENING = "LISTENING"
    WRITING = "WRITING"
    READING_COMPREHENTION = "READING COMPREHENTION"
    GRAMMAR = "GRAMMAR"
     
class EnglishLevel(str, Enum):
    A1 = 'A1'
    A2 = 'A2'
    B1 = 'B1'
    B2 = 'B2'
    C1 = 'C1'
    C2 = 'C2'

class Exercice(Base):
    __tablename__ = "exercice"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(ExerciceType, nullable=False)
    response = Column(String, unique=True, index=True, nullable=False)
    content = Column(String, nullable=False)
    valid = Column(Boolean, nullable=False)
    value = Column(Integer, default=0)
    level = Column(EnglishLevel, nullable=False)

    