import os
import shutil
import sqlite3
import logging
import threading
from contextlib import closing
from sqlite3 import Connection

from src import vocab_db_accessor_wrap

TEST_VOCAB_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '.', 'test_resources', 'vocab.db'))
TEST_FUTURE_TIMESTAMP = vocab_db_accessor_wrap.get_timestamp_ms(2080, 4, 25)  # TODO ill be dead thing

logger = logging.getLogger(__name__)


def get_test_temp_db_file_name(temp_dir: str):
    return os.path.join(temp_dir, 'vocab.db')


def create_temp_db_directory_and_file(base_db_path: str) -> str:
    temp_dir = os.path.join(os.path.dirname(__file__), 'tests_tmp')
    os.makedirs(temp_dir, exist_ok=True)
    shutil.copy(base_db_path, get_test_temp_db_file_name(temp_dir))
    return temp_dir


def remove_temp_db_file(temp_db_file_path: str):
    os.remove(temp_db_file_path)
    logger.info(f"Removed temporary db file: {temp_db_file_path}")


def remove_temp_db_directory(temp_dir: str) -> None:
    shutil.rmtree(temp_dir)
    logger.info(f"Removed temporary directory: {temp_dir}")


def add_word_lookups_to_db_for_non_main_thread(db_file_path: str,
                                               db_update_ready_event: threading.Event,
                                               db_update_processed_event: threading.Event,
                                               stop_event: threading.Event):
    connection_injection = sqlite3.connect(db_file_path)
    # TODO this might not be best here since the majority of old_tests that use it, dont require latest_timestamp table
    vocab_db_accessor_wrap.check_and_create_latest_timestamp_table_if_not_exists(connection_injection)
    add_word_lookups_to_db(connection_injection, db_update_ready_event, db_update_processed_event, stop_event)


def add_word_lookups_to_db(db_connection: Connection,
                           db_update_ready_event: threading.Event,
                           db_update_processed_event: threading.Event,
                           stop_event: threading.Event):
    db_update_ready_event.wait()
    logger.info("Received db_update_ready_event")
    try:
        with closing(db_connection.cursor()) as cursor:
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
        db_connection.commit()
        db_update_processed_event.wait()
        logger.info("Received db_update_processed_event")
    except sqlite3.Error as e:
        logger.info(f"Database error: {e}")
    except Exception as e:
        logger.info(f"Exception in _query: {e}")
    finally:
        db_connection.close()
        stop_event.set()
        logger.info("stop_event set")
