# tests/conftest.py

import pytest
from app import create_app, db
import os

@pytest.fixture(scope='session')
def test_app():
    """Fixture to create a test app with a test database."""
    # Setup test environment variables here or load from a .env.test file
    os.environ['FLASK_ENV'] = 'testing'

    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': os.getenv('DATABASE_URL'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })

    # Setup the test database
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
        db.session.remove()

@pytest.fixture(scope='function')
def test_client(test_app):
    """A test client for the app."""
    return test_app.test_client()

@pytest.fixture(scope='session')
def kindle_db_path():
    """Fixture to provide the path to the test Kindle DB."""
    return os.path.abspath('app_tests/test_resources/vocab.db')
