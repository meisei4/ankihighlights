# test_routes.py
import json
import pytest
from flask import Flask
from unittest.mock import Mock, patch
from routes import (register_start_route, register_stop_route,
                    register_note_route, register_process_new_vocab_highlights_route)

app = Flask(__name__)
app.testing = True
ankikindle_module_mock = Mock()
connection_injection_mock = Mock()
ankiconnect_injection_mock = Mock()
stop_event_mock = Mock()
main_thread_mock = Mock()


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_start_process(client):
    register_start_route(app, ankikindle_module_mock, connection_injection_mock,
                         ankiconnect_injection_mock, stop_event_mock, main_thread_mock)

    ankikindle_module_mock.is_running.return_value = False

    response = client.post('/start')
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "Process started"}

    ankikindle_module_mock.is_running.return_value = True

    response = client.post('/start')
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "Process already running"}


def test_stop_process(client):
    register_stop_route(app, ankikindle_module_mock, stop_event_mock, main_thread_mock)

    ankikindle_module_mock.is_running.return_value = False

    response = client.post('/stop')
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "Process not running"}

    ankikindle_module_mock.is_running.return_value = True

    response = client.post('/stop')
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "Process stopped"}


def test_add_or_update(client):
    register_note_route(app, ankikindle_module_mock, ankiconnect_injection_mock)

    response = client.post('/add_or_update_note', json={
        'word_highlight': 'test',
        'deck_name': 'Default',
        'card_type': 'Basic'
    })

    assert response.status_code == 200
    assert json.loads(response.data) == {"note_id": ankikindle_module_mock.add_or_update_note.return_value}


def test_process_new_vocab_highlights(client):
    register_process_new_vocab_highlights_route(app, ankikindle_module_mock,
                                                connection_injection_mock,
                                                ankiconnect_injection_mock)

    with patch("your_module.vocab_db_accessor_wrap.get_latest_timestamp",
               return_value=None) as mock_get_latest_timestamp:
        response = client.post('/process_new_vocab_highlights')

    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "New vocab highlights processed",
                                         "latest_timestamp": ankikindle_module_mock.FIRST_DATE}
    mock_get_latest_timestamp.assert_called_once_with(connection_injection_mock)

    latest_timestamp = 1623483729000
    with patch("your_module.vocab_db_accessor_wrap.get_latest_timestamp",
               return_value=latest_timestamp) as mock_get_latest_timestamp:
        response = client.post('/process_new_vocab_highlights')

    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "New vocab highlights processed",
                                         "latest_timestamp": latest_timestamp}
    mock_get_latest_timestamp.assert_called_once_with(connection_injection_mock)
