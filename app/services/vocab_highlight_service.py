from app.app import logger
from app.models import DBSession
from app.models.latest_timestamp import LatestTimestamp
from app.models.lookup import Lookup
from app.services.anki_service import AnkiService


class VocabHighlightService:

    @staticmethod
    def check_and_create_latest_timestamp_if_not_exists():
        """Check if the latest timestamp exists, if not, create it with a default value."""
        if DBSession.query(LatestTimestamp).count() == 0:
            latest_timestamp = LatestTimestamp(timestamp=0)  # Default timestamp
            DBSession.add(latest_timestamp)
            DBSession.commit()
            logger.info("Table 'latest_timestamp' initialized with default value.")

    @staticmethod
    def get_latest_timestamp():
        """Retrieve the latest timestamp from the database."""
        latest_timestamp_record = DBSession.query(LatestTimestamp).order_by(LatestTimestamp.timestamp.desc()).first()
        return latest_timestamp_record.timestamp if latest_timestamp_record else 0

    @staticmethod
    def set_latest_timestamp(timestamp):
        """Set a new latest timestamp in the database."""
        latest_timestamp_record = LatestTimestamp(timestamp=timestamp)
        DBSession.add(latest_timestamp_record)
        DBSession.commit()

    @staticmethod
    def get_word_lookups_after_timestamp(timestamp):
        """Retrieve all word lookups that occurred after a given timestamp."""
        return DBSession.query(Lookup).filter(Lookup.timestamp > timestamp).all()

    @staticmethod
    def process_new_vocab_highlights(deck_name="DefaultDeck", model_name="Basic"):
        """Process new vocabulary highlights, add them to Anki, and update the latest timestamp."""
        VocabHighlightService.check_and_create_latest_timestamp_if_not_exists()

        latest_timestamp = VocabHighlightService.get_latest_timestamp()
        highlights = VocabHighlightService.get_word_lookups_after_timestamp(latest_timestamp)

        if highlights:
            logger.info(f"New vocab highlights found: {highlights}")
            added_note_ids = AnkiService.add_notes_to_anki(highlights, deck_name, model_name)

            if added_note_ids:
                new_latest_timestamp = max(highlight.timestamp for highlight in highlights)
                VocabHighlightService.set_latest_timestamp(new_latest_timestamp)
                logger.info(f"Updated latest timestamp to: {new_latest_timestamp}")

        return highlights
