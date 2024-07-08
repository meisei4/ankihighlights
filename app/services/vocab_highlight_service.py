from app.app import db, logger
from app.models.models import Lookup, LatestTimestamp
from app.services.anki_service import AnkiService


class VocabHighlightService:

    @staticmethod
    def check_and_create_latest_timestamp_if_not_exists():
        if LatestTimestamp.query.count() == 0:
            latest_timestamp = LatestTimestamp(timestamp=0)  # Default timestamp
            db.session.add(latest_timestamp)
            db.session.commit()
            logger.info("Table 'latest_timestamp' initialized with default value.")

    @staticmethod
    def get_latest_timestamp():
        latest_timestamp_record = LatestTimestamp.query.order_by(LatestTimestamp.timestamp.desc()).first()
        return latest_timestamp_record.timestamp if latest_timestamp_record else 0

    @staticmethod
    def set_latest_timestamp(timestamp):
        latest_timestamp_record = LatestTimestamp(timestamp=timestamp)
        db.session.add(latest_timestamp_record)
        db.session.commit()

    @staticmethod
    def get_word_lookups_after_timestamp(timestamp):
        return Lookup.query.filter(Lookup.timestamp > timestamp).all()

    @staticmethod
    def process_new_vocab_highlights(deck_name="DefaultDeck", model_name="Basic"):
        latest_timestamp = VocabHighlightService.get_latest_timestamp()
        highlights = VocabHighlightService.get_word_lookups_after_timestamp(latest_timestamp)
        if highlights:
            logger.info(f"New vocab highlights found: {highlights}")
            added_note_ids = AnkiService.add_notes_to_anki(highlights, deck_name, model_name)
            if added_note_ids:
                latest_timestamp = max([highlight.timestamp for highlight in highlights])
                VocabHighlightService.set_latest_timestamp(latest_timestamp)
                logger.info(f"Updated latest timestamp to: {latest_timestamp}")
        return highlights
