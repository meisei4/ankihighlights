import os
import pytest
import logging
import sqlite3
import vocab_db_accessor_wrap
from .test_util import TEST_VOCAB_DB_FILE, create_temp_db_directory_and_file, remove_temp_db_directory


def pytest_configure():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s')


logger = logging.getLogger(__name__)  # TODO figure out best practices for package level logger vs module level loggers


@pytest.fixture(scope="function")
def temp_db_directory():
    temp_dir = create_temp_db_directory_and_file(TEST_VOCAB_DB_FILE)
    yield temp_dir
    remove_temp_db_directory(temp_dir)


@pytest.fixture(scope="function")
def db_connection(temp_db_directory: str):
    db_file = os.path.join(temp_db_directory, 'vocab.db')
    conn = sqlite3.connect(db_file)
    try:
        vocab_db_accessor_wrap.check_and_create_latest_timestamp_table_if_not_exists(conn)
        yield conn
    finally:
        conn.close()
