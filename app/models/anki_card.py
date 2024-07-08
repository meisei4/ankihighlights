from sqlalchemy import Integer, Column, String, ForeignKey, BigInteger

from app.models.meta import Base


class AnkiCard(Base):
    __tablename__ = 'anki_card'
    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey('words.id'), nullable=False)
    deck_name = Column(String(255), nullable=False)
    model_name = Column(String(255), nullable=False)
    front = Column(String(255), nullable=False)
    back = Column(String(255), nullable=False)
    anki_card_id = Column(String(255), nullable=False, unique=True)
    usage = Column(String(255), nullable=True)
    timestamp = Column(BigInteger, nullable=False)

