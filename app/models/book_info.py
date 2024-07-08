from sqlalchemy import Integer, Column, String
from sqlalchemy.orm import relationship

from app.models.meta import Base


class BookInfo(Base):
    __tablename__ = 'book_info'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    authors = Column(String(255), nullable=False)
    lookups = relationship('Lookup', backref='book', lazy=True, cascade="all, delete-orphan")
