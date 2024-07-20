from app.models.lookup import Lookup

class LookupDTO:
    @staticmethod
    def to_dict(lookup: Lookup) -> dict:
        return {
            'id': lookup.id,
            'word_id': lookup.word_id,
            'book_id': lookup.book_id,
            'usage': lookup.usage,
            'timestamp': lookup.timestamp,
        }

    @staticmethod
    def from_dict(data: dict) -> Lookup:
        return Lookup(
            id=data.get('id'),
            word_id=data.get('word_id'),
            book_id=data.get('book_id'),
            usage=data.get('usage'),
            timestamp=data.get('timestamp')
        )
