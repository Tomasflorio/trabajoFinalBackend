from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean
from app.db.session import Base

class Thematic(str, Enum):
    ALGO = "TBD"



class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    thematic = Column(Thematic, nullable=False)
    link = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    img = Column(String, nullable=False)
    
    