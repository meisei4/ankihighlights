import logging
import os

import pytest

from app.app import create_app, db
from config import load_environment


def pytest_configure():
    load_environment()
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)


@pytest.fixture(scope='session')
def test_app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': os.getenv('DATABASE_URL'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'VERSION': int(os.getenv('VERSION'))
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
        db.session.remove()


@pytest.fixture(scope='function')
def test_client(test_app):
    return test_app.test_client()
