import os
import json
import pytest
import sqlite3
import threading
import vocab_db_accessor_wrap
from tests import test_util
from sqlite3 import Connection
from tests.test_util import create_temp_db_directory, add_word_lookups_to_db


# TODO figure out the remote db thing, and how to have that be reflected


# TODO figure out how to clean up with out file access issues
@pytest.fixture(scope="module")
def db_connection():
    temp_dir = test_util.create_temp_db_directory()
    db_file = os.path.join(temp_dir, 'vocab.db')
    with sqlite3.connect(db_file) as conn:
        vocab_db_accessor_wrap.check_and_create_latest_timestamp_table_if_not_exists(conn)
        yield conn


def test_get_all_word_look_ups_after_timestamp():
    test_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2023, 4, 28)
    db_update_ready_event = threading.Event()
    db_update_ready_event.set()
    db_update_processed_event = threading.Event()
    db_update_processed_event.set()
    stop_event = threading.Event()
    temp_db_directory = create_temp_db_directory()
    add_word_lookups_to_db(temp_db_directory, db_update_ready_event, db_update_processed_event, stop_event)
    with sqlite3.connect(os.path.join(temp_db_directory, 'vocab.db')) as conn:
        result = vocab_db_accessor_wrap.get_word_lookups_after_timestamp(conn, test_timestamp)
        assert len(result) == 1
        assert result[0]["word"] == "日本語"
        assert result[0]["usage"] == "日本語の例文"
        assert result[0]["title"] == "日本の本"
        assert result[0]["authors"] == "著者A"


def test_get_table_info():
    temp_db_directory = create_temp_db_directory()
    with sqlite3.connect(os.path.join(temp_db_directory, 'vocab.db')) as conn:
        table_info = vocab_db_accessor_wrap.get_table_info(conn)
        print(json.dumps(table_info, indent=2))
        assert table_info is not None


def test_set_latest_timestamp(db_connection: Connection):
    with db_connection:
        first_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2035, 5, 5)
        vocab_db_accessor_wrap.set_latest_timestamp(db_connection, first_timestamp)
        cursor = db_connection.cursor()
        cursor.execute("SELECT timestamp FROM latest_timestamp ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        assert row[0] == first_timestamp

        second_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2030, 5, 5)
        vocab_db_accessor_wrap.set_latest_timestamp(db_connection, second_timestamp)
        cursor = db_connection.cursor()
        cursor.execute("SELECT count(*) FROM latest_timestamp")
        row = cursor.fetchone()
        assert row[0] == 2  # the second timestamp gets added

        cursor.execute("SELECT timestamp FROM latest_timestamp ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        # second timestamp was inserted after but since first timestamp is later chronologically, first is still fetched
        assert row[0] == first_timestamp


def test_get_latest_timestamp(db_connection: Connection):
    with db_connection:
        remove_latest_timestamp_table(db_connection)
        zeroth_timestamp = vocab_db_accessor_wrap.get_latest_timestamp(db_connection)
        assert not zeroth_timestamp

        vocab_db_accessor_wrap.check_and_create_latest_timestamp_table_if_not_exists(db_connection)
        first_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2035, 5, 5)
        vocab_db_accessor_wrap.set_latest_timestamp(db_connection, first_timestamp)
        actual_timestamp = vocab_db_accessor_wrap.get_latest_timestamp(db_connection)
        assert actual_timestamp == first_timestamp

        second_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2030, 5, 5)
        vocab_db_accessor_wrap.set_latest_timestamp(db_connection, second_timestamp)
        cursor = db_connection.cursor()
        cursor.execute("SELECT count(*) FROM latest_timestamp")
        row = cursor.fetchone()
        assert row[0] == 2  # the second timestamp gets added

        actual_timestamp = vocab_db_accessor_wrap.get_latest_timestamp(db_connection)
        # second timestamp was inserted after but since first timestamp is later chronologically, first is still fetched
        assert actual_timestamp == first_timestamp

        third_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2038, 5, 5)
        vocab_db_accessor_wrap.set_latest_timestamp(db_connection, third_timestamp)
        cursor = db_connection.cursor()
        cursor.execute("SELECT count(*) FROM latest_timestamp")
        row = cursor.fetchone()
        assert row[0] == 3  # the third timestamp gets added

        actual_timestamp = vocab_db_accessor_wrap.get_latest_timestamp(db_connection)
        # third timestamp is later chronologically than both first ands second, thus third is fetched
        assert actual_timestamp == third_timestamp


def test_check_and_create_latest_timestamp_table(db_connection: Connection):
    with db_connection:
        vocab_db_accessor_wrap.check_and_create_latest_timestamp_table_if_not_exists(db_connection)
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='latest_timestamp'
        """)
        table_exists = cursor.fetchone() is not None
        assert table_exists

        remove_latest_timestamp_table(db_connection)
        vocab_db_accessor_wrap.check_and_create_latest_timestamp_table_if_not_exists(db_connection)
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='latest_timestamp'
        """)
        table_exists = cursor.fetchone() is not None
        assert table_exists


def remove_latest_timestamp_table(db_connection: Connection):
    with db_connection:
        cursor = db_connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS latest_timestamp")
        db_connection.commit()


def remove_vocab_lookup_insert(db_connection: Connection):
    with db_connection:
        cursor = db_connection.cursor()
        cursor.execute("DELETE FROM WORDS WHERE id = '1234'")
        cursor.execute("DELETE FROM BOOK_INFO WHERE id = '1234'")
        cursor.execute("DELETE FROM LOOKUPS WHERE id = '1351'")
        db_connection.commit()


