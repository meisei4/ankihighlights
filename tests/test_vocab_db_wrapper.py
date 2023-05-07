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
TEST_FUTURE_TIMESTAMP = vocab_db_accessor_wrap.get_timestamp_ms(2080, 4, 25)   #  TODO probability is i will be dead and thus not my problem


@pytest.mark.skip(reason="test is for kindle mounting only")
def test_copy_to_backup_and_tmp_infinitely():
    vocab_db_accessor_wrap.copy_vocab_db_to_backup_and_tmp_upon_proper_access(0, "")
    shutil.rmtree(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backup')))


@pytest.fixture(scope='function')
def main_thread_test_db_connection():
    with sqlite3.connect(TEST_VOCAB_DB_FILE) as conn:
        vocab_db_accessor_wrap.check_and_create_latest_timestamp_table_if_not_exists(conn)
        yield conn
        remove_latest_timestamp_table(conn)
        remove_vocab_lookup_insert(conn)


def test_get_table_info(main_thread_test_db_connection: Connection):
    with main_thread_test_db_connection:
        table_info = vocab_db_accessor_wrap.get_table_info(main_thread_test_db_connection)
        print(json.dumps(table_info, indent=2))
        assert table_info is not None


def test_get_all_word_look_ups_after_timestamp(main_thread_test_db_connection: Connection):
    test_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2023, 4, 28)
    db_update_ready_event = threading.Event()
    db_update_ready_event.set()
    db_update_processed_event = threading.Event()
    db_update_processed_event.set()
    stop_event = threading.Event()
    add_word_lookups_to_db(db_update_ready_event, db_update_processed_event, stop_event)
    result = vocab_db_accessor_wrap.get_word_lookups_after_timestamp(main_thread_test_db_connection, test_timestamp)

    assert len(result) == 1
    assert result[0]["word"] == "日本語"
    assert result[0]["usage"] == "日本語の例文"
    assert result[0]["title"] == "日本の本"
    assert result[0]["authors"] == "著者A"


def test_set_latest_timestamp(main_thread_test_db_connection: Connection):
    with main_thread_test_db_connection:
        first_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2035, 5, 5)
        vocab_db_accessor_wrap.set_latest_timestamp(main_thread_test_db_connection, first_timestamp)
        cursor = main_thread_test_db_connection.cursor()
        cursor.execute("SELECT timestamp FROM latest_timestamp ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        assert row[0] == first_timestamp

        second_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2030, 5, 5)
        vocab_db_accessor_wrap.set_latest_timestamp(main_thread_test_db_connection, second_timestamp)
        cursor = main_thread_test_db_connection.cursor()
        cursor.execute("SELECT count(*) FROM latest_timestamp")
        row = cursor.fetchone()
        assert row[0] == 2  # the second timestamp gets added

        cursor.execute("SELECT timestamp FROM latest_timestamp ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        # second timestamp was inserted after but since first timestamp is later chronologically, first is still fetched
        assert row[0] == first_timestamp


def test_get_latest_timestamp(main_thread_test_db_connection: Connection):
    with main_thread_test_db_connection:
        remove_latest_timestamp_table(main_thread_test_db_connection)
        zeroth_timestamp = vocab_db_accessor_wrap.get_latest_timestamp(main_thread_test_db_connection)
        assert not zeroth_timestamp

        vocab_db_accessor_wrap.check_and_create_latest_timestamp_table_if_not_exists(main_thread_test_db_connection)
        first_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2035, 5, 5)
        vocab_db_accessor_wrap.set_latest_timestamp(main_thread_test_db_connection, first_timestamp)
        actual_timestamp = vocab_db_accessor_wrap.get_latest_timestamp(main_thread_test_db_connection)
        assert actual_timestamp == first_timestamp

        second_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2030, 5, 5)
        vocab_db_accessor_wrap.set_latest_timestamp(main_thread_test_db_connection, second_timestamp)
        cursor = main_thread_test_db_connection.cursor()
        cursor.execute("SELECT count(*) FROM latest_timestamp")
        row = cursor.fetchone()
        assert row[0] == 2  # the second timestamp gets added

        actual_timestamp = vocab_db_accessor_wrap.get_latest_timestamp(main_thread_test_db_connection)
        # second timestamp was inserted after but since first timestamp is later chronologically, first is still fetched
        assert actual_timestamp == first_timestamp

        third_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2038, 5, 5)
        vocab_db_accessor_wrap.set_latest_timestamp(main_thread_test_db_connection, third_timestamp)
        cursor = main_thread_test_db_connection.cursor()
        cursor.execute("SELECT count(*) FROM latest_timestamp")
        row = cursor.fetchone()
        assert row[0] == 3  # the third timestamp gets added

        actual_timestamp = vocab_db_accessor_wrap.get_latest_timestamp(main_thread_test_db_connection)
        # third timestamp is later chronologically than both first ands second, thus third is fetched
        assert actual_timestamp == third_timestamp


def test_check_and_create_latest_timestamp_table(main_thread_test_db_connection: Connection):
    with main_thread_test_db_connection:
        vocab_db_accessor_wrap.check_and_create_latest_timestamp_table_if_not_exists(main_thread_test_db_connection)
        cursor = main_thread_test_db_connection.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='latest_timestamp'
        """)
        table_exists = cursor.fetchone() is not None
        assert table_exists

        remove_latest_timestamp_table(main_thread_test_db_connection)
        vocab_db_accessor_wrap.check_and_create_latest_timestamp_table_if_not_exists(main_thread_test_db_connection)
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='latest_timestamp'
        """)
        table_exists = cursor.fetchone() is not None
        assert table_exists


def remove_latest_timestamp_table(main_thread_test_db_connection: Connection):
    with main_thread_test_db_connection:
        cursor = main_thread_test_db_connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS latest_timestamp")
        main_thread_test_db_connection.commit()


def remove_vocab_lookup_insert(main_thread_test_db_connection: Connection):
    with main_thread_test_db_connection:
        cursor = main_thread_test_db_connection.cursor()
        cursor.execute("DELETE FROM WORDS WHERE id = '1234'")
        cursor.execute("DELETE FROM BOOK_INFO WHERE id = '1234'")
        cursor.execute("DELETE FROM LOOKUPS WHERE id = '1351'")
        main_thread_test_db_connection.commit()


def add_word_lookups_to_db(db_update_ready_event: threading.Event, db_update_processed_event: threading.Event, stop_event: threading.Event):
    with sqlite3.connect(TEST_VOCAB_DB_FILE) as db_update_thread_test_db_connection:
        db_update_ready_event.wait()
        cursor = db_update_thread_test_db_connection.cursor()
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
        db_update_thread_test_db_connection.commit()
        db_update_processed_event.wait()
        stop_event.set()
