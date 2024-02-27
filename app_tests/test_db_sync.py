import os
import shutil
import docker
import pytest
import sqlite3
from sqlalchemy import create_engine
from app.services.kindle_db_sync_service import KindleSyncService
from app_tests import logger

def get_test_temp_db_file_name(temp_dir: str):
    return os.path.join(temp_dir, 'vocab.db')

def create_temp_db_directory_and_file(base_db_path: str) -> str:
    temp_dir = os.path.join(os.path.dirname(__file__), 'tests_tmp')
    os.makedirs(temp_dir, exist_ok=True)
    shutil.copy(base_db_path, get_test_temp_db_file_name(temp_dir))
    return temp_dir

def remove_temp_db_file(temp_db_file_path: str):
    os.remove(temp_db_file_path)
    logger.info(f"Removed temporary db file: {temp_db_file_path}")

def remove_temp_db_directory(temp_dir: str) -> None:
    shutil.rmtree(temp_dir)
    logger.info(f"Removed temporary directory: {temp_dir}")

@pytest.fixture(scope="function")
def temp_db_directory():
    kindle_db_env_path = os.getenv('KINDLE_DB_PATH')
    kindle_db_abs_path = os.path.abspath(kindle_db_env_path)
    temp_dir = create_temp_db_directory_and_file(kindle_db_abs_path)
    yield temp_dir
    remove_temp_db_directory(temp_dir)

@pytest.fixture(scope="session")
def setup_database():
    client = docker.from_env()
    logger.info("Starting PostgreSQL container...")
    container = client.containers.run(
        'postgres',
        environment={
            'POSTGRES_DB': 'book_vocab_db',
            'POSTGRES_USER': 'dumbuser',
            'POSTGRES_PASSWORD': 'dumbpass',
        },
        ports={'5432/tcp': '5432'},
        detach=True,
    )

    # Construct DB URI and create engine
    db_uri = f"postgresql://dumbuser:dumbpass@localhost:5432/book_vocab_db"
    engine = create_engine(db_uri)

    # Optionally, wait for the database to be ready (implement proper check)
    import time
    time.sleep(10)  # Adjust based on your setup

    yield engine  # Provide the engine to the tests

    # Teardown: stop and remove the container
    print("Stopping PostgreSQL container...")
    container.stop()
    container.remove()

@pytest.fixture(scope="function")
def db_connection(temp_db_directory: str):
    db_file = get_test_temp_db_file_name(temp_db_directory)
    conn = sqlite3.connect(db_file)
    try:
        # Assuming vocab_db_accessor_wrap.check_and_create_latest_timestamp_table_if_not_exists(conn) is needed
        yield conn
    finally:
        conn.close()

def test_sync_from_kindle_db(setup_database, db_connection, test_app):
    # Push the application context
    with test_app.app_context():
        # Now using the temporary database for the test
        engine = setup_database

        # Assuming KindleSyncService can accept a connection to the SQLite db
        KindleSyncService.sync_from_kindle_db(db_connection)

        # Perform checks to ensure data was inserted correctly
        with engine.connect() as connection:
            word_count = connection.execute('SELECT COUNT(*) FROM words').scalar()
            book_info_count = connection.execute('SELECT COUNT(*) FROM book_info').scalar()
            lookup_count = connection.execute('SELECT COUNT(*) FROM lookups').scalar()

            assert word_count > 0, "Words should be inserted into the database."
            assert book_info_count > 0, "BookInfos should be inserted into the database."
            assert lookup_count > 0, "Lookups should be inserted into the database."
