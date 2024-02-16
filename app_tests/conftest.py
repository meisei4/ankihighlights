import pytest
from testcontainers.postgres import PostgresContainer
from app import create_app, db
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope='session')
def postgres():
    logger.info("Starting PostgreSQL container...")
    container = PostgresContainer("postgres:latest")
    container.start()
    logger.info("PostgreSQL container started.")
    yield container
    # Cleanup code after yield will run as teardown
    logger.info("Stopping PostgreSQL container...")
    container.stop()
    logger.info("PostgreSQL container stopped.")


@pytest.fixture(scope='function')
def test_app(postgres):
    """Create and configure a new app instance for each test using the initialized PostgreSQL container."""
    # Assuming the db_uri is already set by the session fixture
    db_uri = postgres.get_connection_url()
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': db_uri,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })
    with app.app_context():
        yield app
        db.session.remove()
        db.drop_all()  # Clean up after each test function


@pytest.fixture(scope='function')
def client(test_app):
    """A test client for the app."""
    return test_app.test_client()


@pytest.fixture(scope='function')
def init_database(test_app):
    """Initialize the database for each test."""
    with test_app.app_context():
        db.create_all()
        yield db
        db.drop_all()  # Ensure clean database state for each test
