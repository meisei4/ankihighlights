import logging
import os
import shutil
import sqlite3
import threading
import vocab_db_accessor_wrap

# __file__ is this file, so next command is: get path to this module file, hop out with cd .., then go cd
# resource, then there's the file
TEST_VOCAB_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test_resources', 'vocab.db'))
# TODO probability is i will be dead and thus not my problem
TEST_FUTURE_TIMESTAMP = vocab_db_accessor_wrap.get_timestamp_ms(2080, 4, 25)

# TODO there was a circular dependancy between test_util and conftest, figure out where to put the main logger
logger = logging.getLogger(__name__)


def create_temp_db_directory_and_file(base_db_path: str) -> str:
    temp_dir = os.path.join(os.path.dirname(__file__), 'tests_tmp')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    shutil.copy(base_db_path, os.path.join(temp_dir, 'vocab.db'))
    return temp_dir


def remove_temp_db_file(temp_db_file_path: str):
    os.remove(temp_db_file_path)
    logger.info(f"Removed temporary db file: {temp_db_file_path}")


def remove_temp_db_directory(temp_dir: str) -> None:
    temp_db_file_path = get_test_temp_db_file_name(temp_dir)
    remove_temp_db_file(temp_db_file_path)
    os.rmdir(temp_dir)
    logger.info(f"Removed temporary directory: {temp_dir}")


def get_test_temp_db_file_name(temp_dir: str):
    return os.path.join(temp_dir, 'vocab.db')


def add_word_lookups_to_db(temp_db_file_path: str,
                           db_update_ready_event: threading.Event,
                           db_update_processed_event: threading.Event,
                           stop_event: threading.Event):
    conn = sqlite3.connect(temp_db_file_path)
    try:
        db_update_ready_event.wait()
        cursor = conn.cursor()
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
        conn.commit()
        db_update_processed_event.wait()
        stop_event.set()
    finally:
        conn.close()
