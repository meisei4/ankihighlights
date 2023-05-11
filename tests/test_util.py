import logging
import os
import shutil
import sqlite3
import tempfile
import threading
import vocab_db_accessor_wrap

# __file__ is this file, so next command is: get path to this module file, hop out with cd .., then go cd
# resource, then there's the file
TEST_VOCAB_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'vocab.db'))
TEST_FUTURE_TIMESTAMP = vocab_db_accessor_wrap.get_timestamp_ms(2080, 4, 25)   #  TODO probability is i will be dead and thus not my problem

logging.basicConfig(filename='test_app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_temp_db_directory() -> str:
    temp_dir = tempfile.mkdtemp()
    shutil.copy(TEST_VOCAB_DB_FILE, os.path.join(temp_dir, 'vocab.db'))
    logger.info(f"Created temporary directory: {temp_dir}")
    return temp_dir


def remove_temp_db_directory(temp_dir: str) -> None:
    shutil.rmtree(temp_dir)
    logger.info(f"Removed temporary directory: {temp_dir}")


def add_word_lookups_to_db(temp_db_directory: str,
                           db_update_ready_event: threading.Event,
                           db_update_processed_event: threading.Event,
                           stop_event: threading.Event):

    with sqlite3.connect(os.path.join(temp_db_directory, 'vocab.db')) as conn:
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
