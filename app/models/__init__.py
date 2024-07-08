from app.models.anki_card import AnkiCard
from app.models.meta import DBSession, Base
from app.models.word import Word
from app.models.lookup import Lookup
from app.models.latest_timestamp import LatestTimestamp
from app.models.book_info import BookInfo


def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)


def init_model(engine):
    """Initialize the model with the provided engine."""
    initialize_sql(engine)
