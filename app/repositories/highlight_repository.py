from app.models.lookup import Lookup
from app.models.meta import DBSession


class HighlightRepository:
    def get_word_lookups_after_timestamp(self, timestamp):
        return DBSession.query(Lookup).filter(Lookup.timestamp > timestamp).all()

    def add_lookup(self, lookup):
        DBSession.add(lookup)
        DBSession.commit()
