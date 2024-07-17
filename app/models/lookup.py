from sqlalchemy import ForeignKey, Integer, Column, BigInteger, String, UniqueConstraint
from app.models.meta import Base


class Lookup(Base):
    __tablename__ = 'lookups'
    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey('words.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('book_info.id'), nullable=False)
    usage = Column(String, nullable=False)
    timestamp = Column(BigInteger, nullable=False)

    __table_args__ = (
        UniqueConstraint('word_id', 'usage', 'timestamp', name='uq_word_usage_timestamp'),
    )
