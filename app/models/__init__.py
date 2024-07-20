from app.models.book_info import BookInfo
from app.models.latest_timestamp import LatestTimestamp
from app.models.lookup import Lookup
from app.models.meta import DBSession, Base, initialize_sql
from app.models.word import Word


def init_model(engine):
    """Initialize the model with the provided engine."""
    initialize_sql(engine)
