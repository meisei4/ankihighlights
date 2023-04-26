import os
import shutil
import time
from sqlite3 import Connection


def copy_to_backup_and_tmp_infinitely():
    target_vocab_file_path = "/Volumes/Kindle/system/vocabulary/vocab.db"  # TODO macOS only
    project_root = os.path.dirname(os.path.abspath(__file__))
    backup_dir = os.path.join(project_root, "backup")
    tmp_dir = os.path.join(project_root, "tmp")
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(tmp_dir, exist_ok=True)
    count = 0
    while count < 14:  # random threshold for testing
        if os.path.exists(target_vocab_file_path):
            count += 1
            copy_vocab_db(count, target_vocab_file_path, backup_dir, tmp_dir)
        time.sleep(2)

    shutil.rmtree(tmp_dir)  # TODO just remove this one only used in case backup fails or something? not sure if this


def copy_vocab_db(count: int, vocab_file_path: str, backup_dir: str, tmp_dir: str):
    start_time = time.monotonic()
    shutil.copy(vocab_file_path, backup_dir)
    shutil.copy(vocab_file_path, tmp_dir)
    end_time = time.monotonic()
    elapsed_time = end_time - start_time
    file_size = os.path.getsize(vocab_file_path) / 1024  # Get file size in KB
    print()
    print(f"vocab.db copied to backup and tmp folders for the {count}{ordinal_suffix(count)} time "
          f"(elapsed time: {elapsed_time:.2f}s, file size: {file_size:.2f} KB)")


def get_table_info(db_connection_injection: Connection) -> dict:
    table_info = {}
    with db_connection_injection:
        cursor = db_connection_injection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            table_columns = {}
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for column in columns:
                column_name = column[1]
                data_type = column[2]
                table_columns[column_name] = data_type

            table_info[table_name] = table_columns

    return table_info


# AUXILIARIES
def ordinal_suffix(count: int) -> str:
    if 11 <= count <= 13:
        return "th"
    elif count % 10 == 1:
        return "st"
    elif count % 10 == 2:
        return "nd"
    elif count % 10 == 3:
        return "rd"
    else:
        return "th"

