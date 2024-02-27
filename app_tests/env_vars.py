import os
import pytest
from app_tests import logger


@pytest.mark.env
def test_environment_variables_loaded():
    database_url = os.getenv('DATABASE_URL')
    flask_env = os.getenv('FLASK_ENV')

    if not database_url:
        logger.info("DATABASE_URL is not set. Check your .env files.")
    if not flask_env:
        logger.info("FLASK_ENV is not set. Check your .env files.")
    if flask_env != 'testing':
        logger.info(f"FLASK_ENV should be 'testing', but it's set to '{flask_env}'.")

    assert database_url is not None, "DATABASE_URL is not set. Check your .env files."
    assert flask_env is not None, "FLASK_ENV is not set. Check your .env files."
    assert flask_env == 'testing', f"FLASK_ENV should be 'testing', but it's set to '{flask_env}'."

    logger.info(f"Environment Variables:\nFLASK_ENV={flask_env}\nDATABASE_URL={database_url}")
