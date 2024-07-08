from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.models.meta import Base


class Word(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    word = Column(String(255), nullable=False, unique=True)
    lookups = relationship('Lookup', backref='word', lazy=True, cascade="all, delete-orphan")
    anki_cards = relationship('AnkiCard', backref='word', lazy=True, cascade="all, delete-orphan")
