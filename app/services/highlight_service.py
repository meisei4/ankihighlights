from injector import inject

from app.anki_constants import CUSTOM_CARD_MODEL_NAME
from app.logger import logger
from app.repositories.highlight_repository import HighlightRepository
from app.repositories.latest_timestamp_repository import LatestTimestampRepository
from app.services.ankiconnect_service import AnkiService


class HighlightService:
    @inject
    def __init__(self, highlight_repository: HighlightRepository,
                 latest_timestamp_repository: LatestTimestampRepository):
        self.highlight_repository = highlight_repository
        self.latest_timestamp_repository = latest_timestamp_repository

    def check_and_create_latest_timestamp_if_not_exists(self):
        self.latest_timestamp_repository.check_and_create_latest_timestamp_if_not_exists()

    def get_latest_timestamp(self):
        return self.latest_timestamp_repository.get_latest_timestamp()

    def set_latest_timestamp(self, timestamp):
        self.latest_timestamp_repository.set_latest_timestamp(timestamp)

    def get_word_lookups_after_timestamp(self, timestamp):
        return self.highlight_repository.get_word_lookups_after_timestamp(timestamp)

    def process_new_vocab_highlights(self, deck_name="DefaultDeck"):
        self.check_and_create_latest_timestamp_if_not_exists()
        latest_timestamp = self.get_latest_timestamp()
        highlights = self.get_word_lookups_after_timestamp(latest_timestamp)

        if highlights:
            logger.info(f"New vocab highlights found: {highlights}")
            added_note_ids = AnkiService.add_notes_to_anki(highlights, deck_name, model_name=CUSTOM_CARD_MODEL_NAME)
            if added_note_ids:
                new_latest_timestamp = max(highlight.timestamp for highlight in highlights)
                self.set_latest_timestamp(new_latest_timestamp)
                logger.info(f"Updated latest timestamp to: {new_latest_timestamp}")

        return highlights
