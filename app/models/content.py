from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship
from .base import Base


class Thematic(str, Enum):
    technology = "technology"
    science = "science"
    literature = "literature"
    art = "art"


# Tabla intermedia para la relación muchos a muchos entre content y users
content_user_assignment = Table(
    'content_user_assignment',
    Base.metadata,
    Column('content_id', Integer, ForeignKey('content.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)


class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    thematic = Column(SQLEnum(Thematic, name="thematic"), nullable=False)
    link = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    img = Column(String(255), nullable=False)
    
    # Relación muchos a muchos con users - usando lazy='select' para evitar problemas
    assigned_users = relationship("User", secondary=content_user_assignment, back_populates="assigned_content", lazy='select')
    
    