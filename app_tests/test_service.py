from unittest.mock import patch

import pytest

from app.services.anki_service import AnkiService


@pytest.fixture
def mocked_anki_response():
    return {"result": True, "error": None}


@patch('app.services.anki_service.AnkiService.send_request')
def test_request_connection_permission(mock_send_request, mocked_anki_response):
    mock_send_request.return_value = mocked_anki_response
    response = AnkiService.request_connection_permission()
    assert response['result'] is True
