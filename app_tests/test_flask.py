import pytest
from testcontainers.postgres import PostgresContainer

from app import create_app, db as _db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Note: Adjust the create_app call according to your application's factory function
    app = create_app({'TESTING': True, 'DATABASE': 'sqlite:///:memory:'})
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope="session")
def app():
    """Set up Flask application for testing."""
    app = create_app()
    with app.app_context():
        yield app

@pytest.fixture(scope="session")
def db(app):
    """Set up test database."""
    _db.app = app
    _db.create_all()
    yield _db
    _db.drop_all()

@pytest.fixture(scope="function")
def session(db):
    """Set up database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    yield session

    transaction.rollback()
    connection.close()
    session.remove()

@pytest.fixture(scope="session")
def postgres():
    """Start a PostgreSQL container for testing."""
    with PostgresContainer("postgres:latest") as postgres:
        yield postgres

# Example test using the session fixture
def test_something_with_db(session):
    # Example database operation
    result = session.execute("SELECT 1")
    assert result.fetchone()[0] == 1

# Assuming you have Anki running with AnkiConnect, write tests that interact with it
def test_anki_connect_interaction(client):
    # Directly call AnkiConnect assuming it's available
    response = client.post("http://localhost:8765", json={
        "action": "version",
        "version": 6
    })
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
