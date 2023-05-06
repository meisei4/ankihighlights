import json
import pytest
import sqlite3
from flask import Flask
from unittest.mock import Mock
from tests import test_vocab_db_wrapper
from routes import (register_start_route, register_stop_route, register_note_route,
                    register_process_new_vocab_highlights_route)


ankikindle_module_mock = Mock()
connection_injection_mock = Mock()
ankiconnect_injection_mock = Mock()
vocab_db_accessor_wrap_injection_mock = Mock()
stop_event_mock = Mock()
main_thread_mock = Mock()


@pytest.fixture
def app_context():
    app = Flask(__name__)
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


@pytest.fixture
def client(app_context):
    with app_context.test_client() as client:
        yield client


def test_start_process(client, app_context):
    register_start_route(app_context, ankikindle_module_mock, connection_injection_mock,
                         ankiconnect_injection_mock, stop_event_mock, main_thread_mock)

    ankikindle_module_mock.is_running.return_value = False

    response = client.post('/start')
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "Process started"}

    ankikindle_module_mock.is_running.return_value = True

    response = client.post('/start')
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "Process already running"}


def test_stop_process(client, app_context):
    register_stop_route(app_context, ankikindle_module_mock, stop_event_mock, main_thread_mock)

    ankikindle_module_mock.is_running.return_value = False

    response = client.post('/stop')
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "Process not running"}

    ankikindle_module_mock.is_running.return_value = True

    response = client.post('/stop')
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "Process stopped"}


def test_add_or_update(client, app_context):
    ankikindle_module_mock.add_or_update_note.return_value = 1
    register_note_route(app_context, ankikindle_module_mock, ankiconnect_injection_mock)

    response = client.post('/add_or_update_note', json={
        'word_highlight': 'test',
        'deck_name': 'Default',
        'card_type': 'Basic'
    })

    assert response.status_code == 200
    assert json.loads(response.data) == {"note_id": 1}


def test_process_new_vocab_highlights(client, app_context):
    connection_injection = sqlite3.Connection(test_vocab_db_wrapper.TEST_VOCAB_DB_FILE)
    ankikindle_module_mock.process_new_vocab_highlights.return_value = 1234
    register_process_new_vocab_highlights_route(app_context, ankikindle_module_mock, connection_injection, ankiconnect_injection_mock)

    response = client.post('/process_new_vocab_highlights')
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "New vocab highlights processed", "latest_timestamp": 1234}
