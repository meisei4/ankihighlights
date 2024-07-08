import logging
import os
import pytest
from app.app import create_app
from app.models.meta import DBSession, Base
from config import load_environment
from app.logging_config import configure_logging


def pytest_configure():
    load_environment()
    configure_logging(level=logging.DEBUG)  # Set to DEBUG for tests only


@pytest.fixture(scope='session')
def test_app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': os.getenv('DATABASE_URL'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'VERSION': int(os.getenv('VERSION')),
        'ANKI_API_URL': os.getenv('ANKI_API_URL', 'http://localhost:8765')  # Set default if not provided
    })

    with app.app_context():
        Base.metadata.create_all()
        yield app
        DBSession.remove()
        # TODO debbuger flag that allows you to look at the database after tests
        #  for now just comment the line below
        Base.metadata.drop_all()


@pytest.fixture(scope='function')
def test_client(test_app):
    with test_app.test_client() as client:
        yield client
        DBSession.remove()


@pytest.fixture(scope='function')
def add_lookup_data():
    def _add_lookup_data():
        from app.models.lookup import Lookup
        from app.models.book_info import BookInfo
        from app.models.word import Word
        DBSession.query(Lookup).delete()
        DBSession.query(BookInfo).delete()
        DBSession.query(Word).delete()
        DBSession.commit()

        book = BookInfo(title="日本の本", authors="著者A")
        DBSession.add(book)
        DBSession.commit()

        word = Word(word="日本語")
        DBSession.add(word)
        DBSession.commit()

        word_lookup = Lookup(word_id=word.id, book_id=book.id, usage="日本語の例文", timestamp=1)
        DBSession.add(word_lookup)
        DBSession.commit()

    return _add_lookup_data


@pytest.fixture(scope='function')
def reset_anki():
    def _reset_anki():
        from app.services.anki_service import AnkiService
        deck_name = "test_deck"

        existing_decks = AnkiService.get_all_deck_names()
        if deck_name not in existing_decks:
            AnkiService.create_deck(deck_name)

        note_ids = AnkiService.find_notes(f"deck:{deck_name}")
        if note_ids:
            AnkiService.delete_notes(note_ids)

    return _reset_anki
