from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import declarative_base
from .base import Base


class Thematic(str, Enum):
    technology = "technology"
    science = "science"
    literature = "literature"
    art = "art"



class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    thematic = Column(SQLEnum(Thematic, name="thematic"), nullable=False)
    link = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    img = Column(String(255), nullable=False)
    
    