import json
import os
import shutil
from sqlite3 import Connection
import pytest
import vocab_database_wrapper
import sqlite3

# TODO figure out the remote db thing, and how to have that be reflected

# __file__ is this file, so next command is: get path to this module file, hop out with cd .., then go cd
# resource, then there's the file
TEST_VOCAB_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'vocab.db'))


@pytest.mark.skip(reason="test is for kindle mounting only")
def test_copy_to_backup_and_tmp_infinitely():
    vocab_database_wrapper.copy_to_backup_and_tmp_infinitely()
    shutil.rmtree(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backup')))


def test_get_table_info():
    db_connection = sqlite3.connect(TEST_VOCAB_DB_FILE)
    table_info = vocab_database_wrapper.get_table_info(db_connection)
    print(json.dumps(table_info, indent=2))
    assert table_info is not None


@pytest.fixture(scope='module')
def test_db_connection():
    with sqlite3.connect(TEST_VOCAB_DB_FILE, timeout=20, isolation_level=None, check_same_thread=False) as conn:
        yield conn
        cleanup_test_data(conn)


def test_get_words_by_profileid(test_db_connection: Connection):
    with test_db_connection:
        cursor = test_db_connection.cursor()
        cursor.execute("BEGIN")
        cursor.execute("""
            INSERT INTO WORDS (id, word, stem, lang, category, timestamp, profileid)
            VALUES ('1', 'hello', 'hello', 'en', 1, 123456, 'test'),
                   ('2', 'world', 'world', 'en', 1, 123456, 'test'),
                   ('3', 'foo', 'foo', 'en', 1, 123456, 'test')
        """)
        cursor.execute("COMMIT")
        results = vocab_database_wrapper.get_words_by_profileid(test_db_connection, "test")
        assert len(results) == 3
        assert results[0]["word"] == "hello"
        assert results[1]["word"] == "world"
        assert results[2]["word"] == "foo"


def test_get_book_info_by_asin(test_db_connection: Connection):
    with test_db_connection:
        cursor = test_db_connection.cursor()
        cursor.execute("BEGIN")
        cursor.execute("""
            INSERT INTO BOOK_INFO (id, asin, guid, lang, title, authors)
            VALUES ('1', 'B123', 'G123', 'en', 'Book Title', 'John Smith')
        """)
        cursor.execute("COMMIT")

        results = vocab_database_wrapper.get_book_info_by_asin(test_db_connection, "B123")
        assert len(results) == 1
        assert results[0]["title"] == "Book Title"
        assert results[0]["authors"] == "John Smith"


def cleanup_test_data(connection: Connection):
    with connection:
        cursor = connection.cursor()
        cursor.execute("BEGIN")
        cursor.execute("DELETE FROM BOOK_INFO WHERE asin = 'B123'")
        cursor.execute("DELETE FROM WORDS WHERE profileid='test'")
        cursor.execute("COMMIT")
