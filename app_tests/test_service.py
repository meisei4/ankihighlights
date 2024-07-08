import logging

from app.models import DBSession
from app.models.latest_timestamp import LatestTimestamp
from app.services.anki_service import AnkiService
from app.services.vocab_highlight_service import VocabHighlightService

logger = logging.getLogger(__name__)


def test_process_new_vocab_highlights(test_client, add_lookup_data, reset_anki):
    logger.info("Starting test_process_new_vocab_highlights")
    # First, reset the Anki environment
    logger.info("Resetting Anki environment")
    reset_anki()

    # Add lookup data to the database
    logger.info("Adding lookup data")
    add_lookup_data()

    # Initialize LatestTimestamp
    logger.info("Initializing LatestTimestamp")
    latest_timestamp = 0
    DBSession.query(LatestTimestamp).delete()
    DBSession.add(LatestTimestamp(timestamp=latest_timestamp))
    DBSession.commit()

    # Process new vocab highlights
    logger.info("Processing new vocab highlights")
    highlights = VocabHighlightService.process_new_vocab_highlights(deck_name="test_deck", model_name="Basic")

    # Verify new highlights were processed
    logger.info("Verifying new highlights processed")
    assert len(highlights) > 0

    # Verify LatestTimestamp is updated
    logger.info("Verifying LatestTimestamp is updated")
    new_latest_timestamp = VocabHighlightService.get_latest_timestamp()
    assert new_latest_timestamp > latest_timestamp

    # Verify notes added to Anki
    logger.info("Verifying notes added to Anki")
    notes = AnkiService.find_notes("deck:test_deck")
    assert len(notes) > 0

    # Verify that the note has the correct content
    logger.info("Verifying note content")
    notes_info = AnkiService.get_notes_info(notes)
    assert notes_info[0]['fields']['Front']['value'] == "日本語"
    logger.info("test_process_new_vocab_highlights completed successfully")
