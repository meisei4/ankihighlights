import logging
import os
from datetime import datetime
from sqlite3 import IntegrityError

import pytest
from flask_injector import FlaskInjector

from app.app import create_app, configure
from app.injection_dependencies import Dependencies
from app.models import LatestTimestamp
from app.models.book_info import BookInfo
from app.models.lookup import Lookup
from app.models.meta import DBSession, Base
from app.models.word import Word
from config import load_environment


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
        Base.metadata.create_all()
        FlaskInjector(app=app, modules=[configure])
        yield app
        DBSession.remove()
        Base.metadata.drop_all()


@pytest.fixture(scope='function')
def test_client(test_app):
    with test_app.test_client() as client:
        yield client
        DBSession.remove()


@pytest.fixture(scope='function')
def add_lookup_data():
    def _add_lookup_data(word="日本語", usage="日本語の例文"):
        from app.models.meta import DBSession
        from app.models.lookup import Lookup
        from app.models.book_info import BookInfo

        word_id = get_or_create_word(word)

        book = BookInfo(title="日本の本", authors="著者A")
        DBSession.add(book)
        DBSession.commit()

        current_timestamp = int(datetime.now().timestamp())

        word_lookup = Lookup(word_id=word_id, book_id=book.id, usage=usage, timestamp=current_timestamp)
        DBSession.add(word_lookup)
        DBSession.commit()

    return _add_lookup_data


def get_or_create_word(word):
    existing_word = DBSession.query(Word).filter_by(word=word).first()
    if existing_word:
        return existing_word.id
    else:
        try:
            new_word = Word(word=word)
            DBSession.add(new_word)
            DBSession.commit()
            return new_word.id
        except IntegrityError:
            DBSession.rollback()
            existing_word = DBSession.query(Word).filter_by(word=word).first()
            return existing_word.id


@pytest.fixture(scope='function')
def reset_anki():
    def _reset_anki():
        from app.services.ankiconnect_service import AnkiService
        deck_name = "test_deck"

        existing_decks = AnkiService.get_all_deck_names()
        if deck_name not in existing_decks:
            AnkiService.create_deck(deck_name)

        note_ids = AnkiService.find_notes(f"deck:{deck_name}")
        if note_ids:
            AnkiService.delete_notes(note_ids)

        DBSession.query(Lookup).delete()
        DBSession.query(BookInfo).delete()
        DBSession.query(Word).delete()

        latest_timestamp = 0
        DBSession.query(LatestTimestamp).delete()
        DBSession.add(LatestTimestamp(timestamp=latest_timestamp))
        DBSession.commit()

    return _reset_anki


@pytest.fixture(scope='function')
def deps(test_app):
    with test_app.app_context():
        injector = FlaskInjector(app=test_app, modules=[configure])
        yield injector.injector.get(Dependencies)
