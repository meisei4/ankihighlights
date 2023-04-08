import json
import ankisync2
import pytest
import requests
from .. import ankikindle
from unittest.mock import patch, Mock, call


@pytest.fixture
def mock_anki_connect():
    with patch('ankisync2.ankiconnect') as mock_ac:
        yield mock_ac.return_value


def test_parse_notes():
    notes = [{"annotationId": "ABCDEFGH1234",
              "highlight": "狐につままれ",
              "location": {"value": 4, "type": "page"},
              "sentence": "若槻は狐につままれたような面持ちで確認した。",
              "note": ""}]
    expected_cards = [{'sentence': '若槻は狐につままれたような面持ちで確認した。', 'word': '狐につままれ'}]
    assert ankikindle.parse_notes(notes) == expected_cards


def test_build_card_from_note():
    note = {"annotationId": "ABCDEFGH1234",
            "highlight": "狐につままれ",
            "location": {"value": 4, "type": "page"},
            "sentence": "若槻は狐につままれたような面持ちで確認した。",
            "note": ""}
    expected_card = {'sentence': '若槻は狐につままれたような面持ちで確認した。', 'word': '狐につままれ'}
    assert ankikindle.build_card_from_note(note) == expected_card


def test_add_and_remove_cards_to_anki_not_mocking():
    deck_name = "mail suck in japan"
    model_name = "aedict"

    # Replace these values with actual cards to add to Anki
    cards = [
        {'sentence': '若槻は狐につままれたような面持ちで確認した。', 'word': '狐につままれ'}
    ]

    # Call the method being tested with the provided arguments
    card_ids = ankikindle.add_cards_to_anki(cards, deck_name, model_name)

    # Confirm that the cards were added to the deck
    connection = ankisync2.ankiconnect('requestPermission')
    note_ids = connection.findNotes(f'deck:"{deck_name}"')
    for card_id in card_ids:
        assert card_id in note_ids

    ankikindle.remove_cards_from_anki(card_ids)

    note_ids = connection.findNotes(f'deck:"{deck_name}"')
    for card_id in card_ids:
        assert card_id not in note_ids

    connection.disconnect()


def test_add_cards_to_anki():
    # Create a mock AnkiConnect instance and set its return values
    mock_anki = Mock()
    mock_anki.deckList.return_value = [{'name': 'Default', 'id': 1}]
    mock_anki.modelList.return_value = [{'name': 'Basic', 'id': 2}]
    mock_anki.invoke.side_effect = [{'result': True}, {'noteId': 1}, {'noteId': 2}]

    # Mock the ankisync2.ankiconnect method to return the mock AnkiConnect instance
    ankisync2.ankiconnect = Mock(return_value=mock_anki)

    cards = [{'sentence': 'Example sentence', 'word': 'example'},
             {'sentence': 'Another example', 'word': 'another'}]

    ankikindle.add_cards_to_anki(cards, 'Default', 'Basic')

    # Verify that AnkiConnect methods were called correctly
    mock_anki.connect.assert_called_once_with()
    mock_anki.invoke.assert_has_calls([
        call('authorize', username='username', password='password'),
        call('addNote', note={'deckName': 'Default', 'modelName': 'Basic',
                              'fields': {'Front': 'Example sentence', 'Back': 'example'}, 'tags': ['kindle']}),
        call('addNote', note={'deckName': 'Default', 'modelName': 'Basic',
                              'fields': {'Front': 'Another example', 'Back': 'another'}, 'tags': ['kindle']})
    ])
    mock_anki.disconnect.assert_called_once_with()


def test_main(monkeypatch):
    mock_response = [{"asin": "B08R7GSGYF",
                      "lastUpdatedDate": 1649529364,
                      "authors": ["貴志祐介"],
                      "title": "黒い家",
                      "notes": [
                          {"annotationId": "ABCDEFGH1234",
                           "highlight": "狐につままれ",
                           "location": {"value": 4, "type": "page"},
                           "sentence": "若槻は狐につままれたような面持ちで確認した。",
                           "note": ""}]}]
    expected_cards = [{'sentence': '若槻は狐につままれたような面持ちで確認した。', 'word': '狐につままれ'}]

    def mock_parse_notes(notes):
        return expected_cards

    monkeypatch.setattr(ankikindle, "parse_notes", mock_parse_notes)

    # Mock out requests.get to return the expected response
    def mock_requests_get(url, headers):
        return MockResponse(json.dumps(mock_response))

    monkeypatch.setattr(requests, "get", mock_requests_get)

    assert ankikindle.main() is None


class MockResponse:
    def __init__(self, content):
        self.content = content

    def json(self):
        return json.loads(self.content)
