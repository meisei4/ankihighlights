import threading
#  TODO why do the fixtures not get explicitly imported from conftest?
# from .conftest import temp_db_directory, db_connection
from sqlite3 import Connection
from contextlib import closing
from .test_util import add_word_lookups_to_db_for_non_main_thread, get_test_temp_db_file_name
from ..old_src import vocab_db_accessor_wrap


def test_get_all_word_look_ups_after_timestamp(db_connection: Connection, temp_db_directory: str):
    try:
        test_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2023, 4, 28)
        db_update_ready_event = threading.Event()
        db_update_ready_event.set()
        db_update_processed_event = threading.Event()
        db_update_processed_event.set()
        stop_event = threading.Event()
        temp_db_file_path = get_test_temp_db_file_name(temp_db_directory)
        add_word_lookups_to_db_for_non_main_thread(temp_db_file_path, db_update_ready_event, db_update_processed_event, stop_event)
        result = vocab_db_accessor_wrap.get_word_lookups_after_timestamp(db_connection, test_timestamp)
        assert len(result) == 1
        assert result[0]["word"] == "日本語"
        assert result[0]["usage"] == "日本語の例文"
        assert result[0]["title"] == "日本の本"
        assert result[0]["authors"] == "著者A"
        db_connection.commit()  # TODO figure out how to do the best/most transparent practice with all these commit and closes

    finally:
        db_connection.close()


def test_set_latest_timestamp(db_connection: Connection):
    try:
        first_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2035, 5, 5)
        with closing(db_connection.cursor()) as cursor:  # Close cursor automatically
            vocab_db_accessor_wrap.set_latest_timestamp(db_connection, first_timestamp)
            cursor.execute("SELECT timestamp FROM latest_timestamp ORDER BY timestamp DESC LIMIT 1")
            row = cursor.fetchone()
            assert row[0] == first_timestamp

            second_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2030, 5, 5)
            vocab_db_accessor_wrap.set_latest_timestamp(db_connection, second_timestamp)
            cursor.execute("SELECT count(*) FROM latest_timestamp")
            row = cursor.fetchone()
            assert row[0] == 2  # the second timestamp gets added

            cursor.execute("SELECT timestamp FROM latest_timestamp ORDER BY timestamp DESC LIMIT 1")
            row = cursor.fetchone()
            # second timestamp was inserted after but since first timestamp is later chronologically, first is
            # still fetched
            assert row[0] == first_timestamp
        db_connection.commit()  # commit changes to the dbted after but since first timestamp is later chronologically,
        # first is still fetched
    finally:
        db_connection.close()


def test_get_latest_timestamp(db_connection: Connection):
    try:
        with closing(db_connection.cursor()) as cursor:
            zeroth_timestamp = vocab_db_accessor_wrap.get_latest_timestamp(db_connection)
            assert not zeroth_timestamp

            first_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2035, 5, 5)
            vocab_db_accessor_wrap.set_latest_timestamp(db_connection, first_timestamp)
            actual_timestamp = vocab_db_accessor_wrap.get_latest_timestamp(db_connection)
            assert actual_timestamp == first_timestamp

            second_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2030, 5, 5)
            vocab_db_accessor_wrap.set_latest_timestamp(db_connection, second_timestamp)
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
        db_connection.commit()
    finally:
        db_connection.close()


def test_check_and_create_latest_timestamp_table(db_connection: Connection):
    with closing(db_connection.cursor()) as cursor:
        vocab_db_accessor_wrap.check_and_create_latest_timestamp_table_if_not_exists(db_connection)
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
    db_connection.commit()


def remove_latest_timestamp_table(db_connection: Connection):
    with closing(db_connection.cursor()) as cursor:  # Close cursor automatically
        cursor.execute("DROP TABLE IF EXISTS latest_timestamp")
    db_connection.commit()  # commit changes to the db


def remove_vocab_lookup_insert(db_connection: Connection):
    with closing(db_connection.cursor()) as cursor:  # Close cursor automatically
        cursor.execute("DELETE FROM WORDS WHERE id = '1234'")
        cursor.execute("DELETE FROM BOOK_INFO WHERE id = '1234'")
        cursor.execute("DELETE FROM LOOKUPS WHERE id = '1351'")
    db_connection.commit()  # commit changes to the db
