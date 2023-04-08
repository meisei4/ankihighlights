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


def test_add_and_remove_cards_to_anki():
    deck_name = "mail sucks in japan"
    model_name = "aedict"
    cards = [
        {'sentence': '若槻は狐につままれたような面持ちで確認した。', 'word': '狐につままれ'}
    ]
    added_note_ids = ankikindle.add_notes_to_anki(cards, deck_name, model_name)

    all_note_ids = ankisync2.ankiconnect('findNotes', query=f'deck:"{deck_name}"')
    for note_id in added_note_ids:
        assert note_id in all_note_ids

    ankikindle.remove_notes_from_anki(added_note_ids)

    note_ids = ankisync2.ankiconnect('findNotes', query=f'deck:"{deck_name}"')
    for note_id in added_note_ids:
        assert note_id not in note_ids

#TODO this is somehow now a proper mock of the ankiconnect api

def test_add_cards_to_anki_mocked():
    mock_anki = Mock()
    mock_anki.ankiconnect.return_value = {'permission': 'granted'}
    mock_anki.ankiconnect.side_effect = [
        {'permission': 'granted'},  # requestPermission
        [{'name': 'Default', 'id': 1}],  # deckNames
        [{'name': 'Basic', 'id': 2}],  # modelNames
        {'result':  101},  # addNote for first card
        {'result': 102}  # addNote for second card
    ]

    ankisync2.ankiconnect = mock_anki.ankiconnect

    cards = [{'sentence': 'Example sentence', 'word': 'example'},
             {'sentence': 'Another example', 'word': 'another'}]

    added_note_ids = ankikindle.add_notes_to_anki(cards, 'Default', 'Basic')

    assert added_note_ids == [101, 102]

#TODO old test now, figure out once all other unit tests are finished
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
