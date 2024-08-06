import os
import shutil
import sqlite3

import pytest
from sqlalchemy import create_engine

from app_tests import logger
from flask_injector import FlaskInjector
from app.injection_dependencies import Dependencies
from app.app import configure


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


@pytest.fixture(scope="function")
def temp_db_directory():
    ebook_db_env_path = os.getenv('EBOOK_DB_PATH')
    ebook_db_abs_path = os.path.abspath(ebook_db_env_path)
    temp_dir = create_temp_db_directory_and_file(ebook_db_abs_path)
    yield temp_dir
    remove_temp_db_directory(temp_dir)


@pytest.fixture(scope="session")
def setup_database():
    db_uri = "postgresql://dumbuser:dumbpass@localhost:5432/reduced_ebook_lookups"
    engine = create_engine(db_uri)

    import time
    time.sleep(5)

    yield engine


@pytest.fixture(scope="function")
def db_connection(temp_db_directory: str):
    db_file = get_test_temp_db_file_name(temp_db_directory)
    conn = sqlite3.connect(db_file)
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture(scope='function')
def deps(test_app):
    with test_app.app_context():
        injector = FlaskInjector(app=test_app, modules=[configure])
        yield injector.injector.get(Dependencies)


# NOTE: THIS REQUIRES THE postgres container to be running (to avoid having to make throwaway containers each test)
def test_sync_from_ebook_db(setup_database, db_connection, test_app, deps: Dependencies):
    with test_app.app_context():
        engine = setup_database

        deps.ebook_db_sync_service.sync_from_ebook_db(db_connection)

        with engine.connect() as connection:
            word_count = connection.execute('SELECT COUNT(*) FROM words').scalar()
            book_info_count = connection.execute('SELECT COUNT(*) FROM book_info').scalar()
            lookup_count = connection.execute('SELECT COUNT(*) FROM lookups').scalar()

            assert word_count > 0, "Words should be inserted into the database."
            assert book_info_count > 0, "BookInfos should be inserted into the database."
            assert lookup_count > 0, "Lookups should be inserted into the database."
