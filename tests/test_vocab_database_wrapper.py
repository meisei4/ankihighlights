import json
import os
import shutil
from datetime import datetime
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
    with sqlite3.connect(TEST_VOCAB_DB_FILE) as conn:
        yield conn
        cleanup_test_data(conn)


def test_get_all_word_look_ups_after_timestamp(test_db_connection: Connection):
    test_timestamp = vocab_database_wrapper.get_timestamp_ms(2030, 4, 25)
    with test_db_connection:
        cursor = test_db_connection.cursor()
        cursor.execute("BEGIN")
        cursor.execute(f"""
            INSERT INTO WORDS (id, word, stem, lang, category, timestamp, profileid) 
            VALUES ('1234', '日本語', '日本', 'ja', 1, {test_timestamp}, 'test')
        """)
        cursor.execute("""
            INSERT INTO BOOK_INFO (id, asin, guid, lang, title, authors) 
            VALUES ('1234', 'B123', 'G456', 'ja', '日本の本', '著者A')
        """)
        cursor.execute(f"""
            INSERT INTO LOOKUPS (id, word_key, book_key, dict_key, pos, usage, timestamp) 
            VALUES ('1351', '1234', '1234', '1', 'n', '日本語の例文', {test_timestamp})
        """)
        cursor.execute("END")
        result = vocab_database_wrapper.get_all_word_look_ups_after_timestamp(test_db_connection, test_timestamp)

        assert len(result) == 1
        assert result[0]["word"] == "日本語"
        assert result[0]["usage"] == "日本語の例文"
        assert result[0]["title"] == "日本の本"
        assert result[0]["authors"] == "著者A"


def cleanup_test_data(connection: Connection):
    with connection:
        cursor = connection.cursor()
        cursor.execute("BEGIN")
        cursor.execute("DELETE FROM BOOK_INFO WHERE asin='B123'")
        cursor.execute("DELETE FROM WORDS WHERE profileid='test'")
        cursor.execute("DELETE FROM LOOKUPS WHERE id='1351'")
        cursor.execute("END")
