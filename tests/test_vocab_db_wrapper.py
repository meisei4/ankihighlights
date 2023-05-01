import os
import json
import shutil
import pytest
import sqlite3
import threading
import vocab_db_accessor_wrap
from sqlite3 import Connection

# TODO figure out the remote db thing, and how to have that be reflected

# __file__ is this file, so next command is: get path to this module file, hop out with cd .., then go cd
# resource, then there's the file
TEST_VOCAB_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'vocab.db'))
TEST_FUTURE_TIMESTAMP = vocab_db_accessor_wrap.get_timestamp_ms(2080, 4, 25)   # TODO probability is i will be dead and thus not my problem

@pytest.mark.skip(reason="test is for kindle mounting only")
def test_copy_to_backup_and_tmp_infinitely():
    vocab_db_accessor_wrap.copy_vocab_db_to_backup_and_tmp_upon_proper_access(0, "")
    shutil.rmtree(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backup')))


def test_get_table_info():
    db_connection = sqlite3.connect(TEST_VOCAB_DB_FILE)
    table_info = vocab_db_accessor_wrap.get_table_info(db_connection)
    print(json.dumps(table_info, indent=2))
    assert table_info is not None


@pytest.fixture(scope='module')
def test_db_connection():
    with sqlite3.connect(TEST_VOCAB_DB_FILE) as conn:
        yield conn
        cleanup_test_data(conn)


def test_get_all_word_look_ups_after_timestamp(test_db_connection: Connection):
    test_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2030, 4, 25)
    simulate_db_update(threading.Event())
    result = vocab_db_accessor_wrap.get_word_lookups_after_timestamp(test_db_connection, test_timestamp)

    assert len(result) == 1
    assert result[0]["word"] == "日本語"
    assert result[0]["usage"] == "日本語の例文"
    assert result[0]["title"] == "日本の本"
    assert result[0]["authors"] == "著者A"


def simulate_db_update(dp_update_flag: threading.Event):
    db_for_update = sqlite3.connect(TEST_VOCAB_DB_FILE)

    with db_for_update as connection:
        cursor = connection.cursor()
        cursor.execute("BEGIN")
        cursor.execute(f"""
                    INSERT INTO WORDS (id, word, stem, lang, category, timestamp, profileid) 
                    VALUES ('1234', '日本語', '日本', 'ja', 1, {TEST_FUTURE_TIMESTAMP}, 'test')
                """)
        cursor.execute("""
                    INSERT INTO BOOK_INFO (id, asin, guid, lang, title, authors) 
                    VALUES ('1234', 'B123', 'G456', 'ja', '日本の本', '著者A')
                """)
        cursor.execute(f"""
                    INSERT INTO LOOKUPS (id, word_key, book_key, dict_key, pos, usage, timestamp) 
                    VALUES ('1351', '1234', '1234', '1', 'n', '日本語の例文', {TEST_FUTURE_TIMESTAMP})
                """)
        cursor.execute("END")
        dp_update_flag.set()


def cleanup_test_data(connection: Connection):
    with connection:
        cursor = connection.cursor()
        cursor.execute("BEGIN")
        cursor.execute("DELETE FROM BOOK_INFO WHERE asin='B123'")
        cursor.execute("DELETE FROM WORDS WHERE profileid='test'")
        cursor.execute("DELETE FROM LOOKUPS WHERE id='1351'")
        cursor.execute("END")
