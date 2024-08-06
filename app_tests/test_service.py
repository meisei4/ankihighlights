import time

import pytest
from flask_injector import FlaskInjector

from app.app import configure
from app.injection_dependencies import Dependencies
from app.services.ankiconnect_service import AnkiService
from app_tests import logger


@pytest.fixture(scope='function')
def deps(test_app):
    with test_app.app_context():
        injector = FlaskInjector(app=test_app, modules=[configure])
        yield injector.injector.get(Dependencies)


def initialize_and_process_highlights(deps: Dependencies, add_lookup_data_func, deck_name="test_deck"):
    add_lookup_data_func()

    # Initialize LatestTimestamp
    logger.info("Initializing LatestTimestamp")

    # Process new vocab highlights
    logger.info("Processing new vocab highlights")
    highlights = deps.highlight_service.process_new_vocab_highlights(deck_name=deck_name)

    # Verify new highlights were processed
    logger.info("Verifying new highlights processed")
    assert len(highlights) > 0

    return highlights


def test_process_new_vocab_highlights(test_client, add_lookup_data, reset_anki, deps: Dependencies):
    logger.info("Starting test_process_new_vocab_highlights")
    # First, reset the Anki environment
    logger.info("Resetting Anki environment")
    reset_anki()

    # Initialize and process highlights
    logger.info("Initializing and processing highlights")
    initialize_and_process_highlights(deps, add_lookup_data)

    # Verify LatestTimestamp is updated
    logger.info("Verifying LatestTimestamp is updated")
    new_latest_timestamp = deps.highlight_service.get_latest_timestamp()
    assert new_latest_timestamp > 0

    # Verify notes added to Anki
    logger.info("Verifying notes added to Anki")
    notes = AnkiService.find_notes("deck:test_deck")
    assert len(notes) > 0

    # Verify that the note has the correct content
    logger.info("Verifying note content")
    notes_info = AnkiService.get_notes_info(notes)
    assert notes_info[0]['fields']['Expression']['value'] == "日本語"
    logger.info("test_process_new_vocab_highlights completed successfully")


def test_update_existing_note_with_new_example(test_client, add_lookup_data, reset_anki, deps: Dependencies):
    logger.info("Starting test_update_existing_note_with_new_example")
    # Reset the Anki environment
    logger.info("Resetting Anki environment")
    reset_anki()

    # Initialize and process highlights
    logger.info("Initializing and processing highlights")
    highlights = initialize_and_process_highlights(deps, add_lookup_data)

    # Add new example sentence for an existing word
    new_example_sentence = "新しい日本語例文"
    word_to_update = highlights[0].word.word

    # Update the database with the new example
    time.sleep(1)  # to have a new timestamp for a unique lookup
    logger.info("ADDING NEW EXAMPLE SENTENCE TO THE ALREADY ADDED WORD---------------------------")
    add_lookup_data(word=word_to_update, usage=new_example_sentence)

    # Process new vocab highlights again
    logger.info("Processing new vocab highlights with new example sentence")
    deps.highlight_service.process_new_vocab_highlights(deck_name="test_deck")

    # Verify that the note was updated with the new example sentence
    logger.info("Verifying note updated with new example sentence")
    notes = AnkiService.find_notes(f"deck:test_deck Expression:{word_to_update}")
    assert len(notes) > 0

    notes_info = AnkiService.get_notes_info(notes)
    assert new_example_sentence in notes_info[0]['fields']['Sentence']['value']

    logger.info("test_update_existing_note_with_new_example completed successfully")
