# test_integration.py
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Base, Word, BookInfo, Lookup
from app import create_app
from app.services.kindle_sync_service import KindleSyncService

# Set the correct environment variables
os.environ['TEST_DATABASE_URI'] = 'postgresql://user:password@localhost:5432/dbname'

# Fixture to set up the Docker Postgres container
@pytest.fixture(scope='session')
def docker_compose_file(pytestconfig):
    return pytestconfig.rootdir / "docker-compose.yml"

# Fixture to set up the Flask app for testing
@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['TEST_DATABASE_URI']
    return app

# Fixture to set up the database session
@pytest.fixture(scope='session')
def db_session(docker_ip, docker_services):
    """Establish a connection to the database and create tables."""
    engine = create_engine(os.environ['TEST_DATABASE_URI'])
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

# Fixture to set up the test Kindle database
@pytest.fixture(scope='session')
def kindle_db_session():
    # Assuming you have a function to create a test SQLite database and populate it
    # For example, a function named `create_test_kindle_db` that returns a session object
    return create_test_kindle_db()

# Test the synchronization logic
def test_full_synchronization(kindle_db_session, db_session):
    # Assuming the kindle_sync_service.sync_from_kindle_db method takes a session as an argument
    KindleSyncService.sync_from_kindle_db(kindle_db_session)

    # Verify that data is now present in the Postgres database
    word_count = db_session.query(Word).count()
    book_info_count = db_session.query(BookInfo).count()
    lookup_count = db_session.query(Lookup).count()

    assert word_count > 0
    assert book_info_count > 0
    assert lookup_count > 0

# Additional old_tests for individual model insertion and verification...

# Remember to define the `create_test_kindle_db` function or equivalent that sets up
# the SQLite database with the structure and data of the example Kindle database.
