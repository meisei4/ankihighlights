import logging
import os
import sqlite3

import pytest

import vocab_db_accessor_wrap
from tests import test_util


def pytest_configure():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s')



@pytest.fixture(scope="module")
def temp_db_directory():
    temp_dir = test_util.create_temp_db_directory_and_file()
    yield temp_dir


# TODO figure out clean up of temp stuff, gpt is unable to figure out why the Permission error happens
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
