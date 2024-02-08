import pytest

from app import create_app, db


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Note: Adjust the create_app call to use a test database
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })

    with app.app_context():
        db.create_all()

    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
