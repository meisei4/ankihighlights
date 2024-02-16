# tests/conftest.py

import pytest
from app import create_app, db

@pytest.fixture(scope='function')
def test_app():
    """Create and configure a new app instance for each test."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(test_app):
    """A test client for the app."""
    return test_app.test_client()

@pytest.fixture(scope='function')
def init_database(test_app):
    """Initialize the database."""
    with test_app.app_context():
        db.create_all()
        yield db
        db.drop_all()
