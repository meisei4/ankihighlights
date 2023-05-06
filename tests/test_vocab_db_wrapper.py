import os
import json
import shutil
import time
import pytest
import sqlite3
import threading
import vocab_db_accessor_wrap
from sqlite3 import Connection

# TODO figure out the remote db thing, and how to have that be reflected

# TODO This only works when running the suite alone (not during a full run of all the tests in the test directory

# __file__ is this file, so next command is: get path to this module file, hop out with cd .., then go cd
# resource, then there's the file
TEST_VOCAB_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'vocab.db'))
TEST_FUTURE_TIMESTAMP = vocab_db_accessor_wrap.get_timestamp_ms(2080, 4, 25)   #  TODO probability is i will be dead and thus not my problem


@pytest.mark.skip(reason="test is for kindle mounting only")
def test_copy_to_backup_and_tmp_infinitely():
    vocab_db_accessor_wrap.copy_vocab_db_to_backup_and_tmp_upon_proper_access(0, "")
    shutil.rmtree(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backup')))


def test_get_table_info():
    db_connection = sqlite3.connect(TEST_VOCAB_DB_FILE)
    table_info = vocab_db_accessor_wrap.get_table_info(db_connection)
    print(json.dumps(table_info, indent=2))
    assert table_info is not None


@pytest.fixture(scope='function')
def test_db_connection_main_thread():
    with sqlite3.connect(TEST_VOCAB_DB_FILE) as conn:
        conn.execute("BEGIN")
        vocab_db_accessor_wrap.check_and_create_latest_timestamp_table(conn)
        yield conn
        conn.rollback()


def test_get_all_word_look_ups_after_timestamp(test_db_connection_main_thread):
    test_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2030, 4, 25)
    add_word_lookups_to_db(threading.Event())
    result = vocab_db_accessor_wrap.get_word_lookups_after_timestamp(test_db_connection_main_thread, test_timestamp)

    assert len(result) == 1
    assert result[0]["word"] == "日本語"
    assert result[0]["usage"] == "日本語の例文"
    assert result[0]["title"] == "日本の本"
    assert result[0]["authors"] == "著者A"


def test_set_latest_timestamp(test_db_connection_main_thread):
    with test_db_connection_main_thread:
        first_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2035, 5, 5)
        vocab_db_accessor_wrap.set_latest_timestamp(test_db_connection_main_thread, first_timestamp)
        cursor = test_db_connection_main_thread.cursor()
        cursor.execute("SELECT timestamp FROM latest_timestamp ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        assert row[0] == first_timestamp

        second_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2030, 5, 5)
        vocab_db_accessor_wrap.set_latest_timestamp(test_db_connection_main_thread, second_timestamp)
        cursor = test_db_connection_main_thread.cursor()
        cursor.execute("SELECT count(*) FROM latest_timestamp")
        row = cursor.fetchone()
        assert row[0] == 2  # the second timestamp gets added

        cursor.execute("SELECT timestamp FROM latest_timestamp ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        # second timestamp was inserted after but since first timestamp is later chronologically, first is still fetched
        assert row[0] == first_timestamp


def test_get_latest_timestamp(test_db_connection_main_thread):
    with test_db_connection_main_thread:
        test_db_connection_main_thread.execute("DROP TABLE IF EXISTS latest_timestamp")
        zeroth_timestamp = vocab_db_accessor_wrap.get_latest_timestamp(test_db_connection_main_thread)
        assert not zeroth_timestamp

        vocab_db_accessor_wrap.check_and_create_latest_timestamp_table(test_db_connection_main_thread)
        first_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2035, 5, 5)
        vocab_db_accessor_wrap.set_latest_timestamp(test_db_connection_main_thread, first_timestamp)
        actual_timestamp = vocab_db_accessor_wrap.get_latest_timestamp(test_db_connection_main_thread)
        assert actual_timestamp == first_timestamp

        second_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2030, 5, 5)
        vocab_db_accessor_wrap.set_latest_timestamp(test_db_connection_main_thread, second_timestamp)
        cursor = test_db_connection_main_thread.cursor()
        cursor.execute("SELECT count(*) FROM latest_timestamp")
        row = cursor.fetchone()
        assert row[0] == 2  # the second timestamp gets added

        actual_timestamp = vocab_db_accessor_wrap.get_latest_timestamp(test_db_connection_main_thread)
        # second timestamp was inserted after but since first timestamp is later chronologically, first is still fetched
        assert actual_timestamp == first_timestamp

        third_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2038, 5, 5)
        vocab_db_accessor_wrap.set_latest_timestamp(test_db_connection_main_thread, third_timestamp)
        cursor = test_db_connection_main_thread.cursor()
        cursor.execute("SELECT count(*) FROM latest_timestamp")
        row = cursor.fetchone()
        assert row[0] == 3  # the third timestamp gets added

        actual_timestamp = vocab_db_accessor_wrap.get_latest_timestamp(test_db_connection_main_thread)
        # third timestamp is later chronologically than both first ands second, thus third is fetched
        assert actual_timestamp == third_timestamp


def test_check_and_create_latest_timestamp_table():
    with sqlite3.connect(TEST_VOCAB_DB_FILE) as conn:
        vocab_db_accessor_wrap.check_and_create_latest_timestamp_table(conn)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='latest_timestamp'
        """)
        table_exists = cursor.fetchone() is not None
        assert table_exists

        cursor.execute("DROP TABLE IF EXISTS latest_timestamp")
        vocab_db_accessor_wrap.check_and_create_latest_timestamp_table(conn)
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='latest_timestamp'
        """)
        table_exists = cursor.fetchone() is not None
        assert table_exists


def add_word_lookups_to_db(connection: Connection, dp_update_flag: threading.Event, sync_condition: threading.Condition):
    with connection:
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
        with sync_condition:
            cursor.execute("END")
            sync_condition.notify_all()

        time.sleep(1)
        dp_update_flag.set()
        # TODO not sure how to control this sleep since it relies heavy on how fast the ankikindle.main while loop
        #  can run, so if that gets new sleeps then this needs to be updated
