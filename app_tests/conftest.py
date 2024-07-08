import logging
import os
import pytest
from app.app import create_app, db
from app.models.models import Lookup, BookInfo, Word
from config import load_environment
from app.services.anki_service import AnkiService


def pytest_configure():
    load_environment()
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@pytest.fixture(scope='session')
def test_app():
    load_environment()
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': os.getenv('DATABASE_URL'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'VERSION': int(os.getenv('VERSION')),
        'ANKI_API_URL': os.getenv('ANKI_API_URL', 'http://localhost:8765')  # Set default if not provided
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def test_client(test_app):
    with test_app.test_client() as client:
        yield client
        db.session.remove()

@pytest.fixture(scope='function')
def add_lookup_data():
    def _add_lookup_data():
        # Clean up existing data
        Lookup.query.delete()
        BookInfo.query.delete()
        Word.query.delete()
        db.session.commit()

        # Create a book record
        book = BookInfo(title="日本の本", authors="著者A")
        db.session.add(book)
        db.session.commit()

        # Create a word record
        word = Word(word="日本語")
        db.session.add(word)
        db.session.commit()

        # Create lookup records associated with the book and word
        word_lookup = Lookup(word_id=word.id, book_id=book.id, usage="日本語の例文", timestamp=1)
        db.session.add(word_lookup)
        db.session.commit()

    return _add_lookup_data


@pytest.fixture(scope='function')
def reset_anki():
    def _reset_anki():
        deck_name = "test_deck"

        # Ensure the deck exists
        existing_decks = AnkiService.get_all_deck_names()
        if deck_name not in existing_decks:
            AnkiService.create_deck(deck_name)

        # Clear all notes from the deck
        note_ids = AnkiService.find_notes(f"deck:{deck_name}")
        if note_ids:
            AnkiService.delete_notes(note_ids)

    return _reset_anki
