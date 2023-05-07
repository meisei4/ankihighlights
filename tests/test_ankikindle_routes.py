import json
import pytest
from flask import Flask
from unittest.mock import Mock
from ankikindle_flask_routes import register_process_new_vocab_highlights_route


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


# TODO figure out how to decide when the db is available, cant pass by injection if the connection is not available yet.
#  only pass when it is, otherwise maybe connect to a temporary db? not sure
@pytest.mark.skip(reason="not ready yet")
def test_process_new_vocab_highlights(client, app_context):
    ankikindle_module_mock.process_new_vocab_highlights.return_value = []
    register_process_new_vocab_highlights_route(app_context, ankikindle_module_mock, ankiconnect_injection_mock)

    response = client.post('/process_new_vocab_highlights')
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "No new vocab highlights to process"}
