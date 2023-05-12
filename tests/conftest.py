import os
import pytest
import logging
import sqlite3
import vocab_db_accessor_wrap
from tests import test_util


def pytest_configure():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s')


logger = logging.getLogger(__name__)  # TODO figure out best practices for package level logger vs module level loggers


@pytest.fixture(scope="module")
def temp_db_directory():
    temp_dir = test_util.create_temp_db_directory_and_file()
    yield temp_dir


# TODO figure out clean up: gpt is unable to help explain why the Permission error happens when trying to remove db dir
@pytest.fixture(scope="function")
def db_connection(temp_db_directory: str):
    db_file = os.path.join(temp_db_directory, 'vocab.db')
    conn = sqlite3.connect(db_file)
    try:
        vocab_db_accessor_wrap.check_and_create_latest_timestamp_table_if_not_exists(conn)
        yield conn
    finally:
        conn.close()

    # test_util.remove_temp_db_directory(temp_db_directory)