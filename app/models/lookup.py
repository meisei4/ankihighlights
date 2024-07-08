from sqlalchemy import ForeignKey, Integer, Column, BigInteger, String

from app.models.meta import Base


class Lookup(Base):
    __tablename__ = 'lookups'
    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey('words.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('book_info.id'), nullable=False)
    usage = Column(String, nullable=False)
    timestamp = Column(BigInteger, nullable=False)
