import json
import ankisync2
import pytest
import requests

from .. import ankikindle
from unittest.mock import patch


@pytest.fixture
def mock_anki_connect():
    with patch('ankisync2.ankiconnect') as mock_ac:
        yield mock_ac.return_value


def test_build_notes():
    notes = [{"annotationId": "ABCDEFGH1234",
              "highlight": "狐につままれ",
              "location": {"value": 4, "type": "page"},
              "sentence": "若槻は狐につままれたような面持ちで確認した。",
              "note": ""}]
    expected_notes = [{'sentence': '若槻は狐につままれたような面持ちで確認した。', 'word': '狐につままれ'}]
    assert ankikindle.build_notes(notes) == expected_notes


def test_build_note():
    note = {"annotationId": "ABCDEFGH1234",
            "highlight": "狐につままれ",
            "location": {"value": 4, "type": "page"},
            "sentence": "若槻は狐につままれたような面持ちで確認した。",
            "note": ""}
    expected_note = {'sentence': '若槻は狐につままれたような面持ちで確認した。', 'word': '狐につままれ'}
    assert ankikindle.build_note(note) == expected_note


def test_add_and_remove_notes_to_anki():
    deck_name = "mail sucks in japan"
    model_name = "aedict"
    notes = [
        {'sentence': '若槻は狐につままれたような面持ちで確認した。', 'word': '狐につままれ'}
    ]
    added_note_ids = ankikindle.add_notes_to_anki(notes, deck_name, model_name)

    all_note_ids = ankisync2.ankiconnect('findNotes', query=f'deck:"{deck_name}"')
    for note_id in added_note_ids:
        assert note_id in all_note_ids

    ankikindle.remove_notes_from_anki(added_note_ids)

    note_ids = ankisync2.ankiconnect('findNotes', query=f'deck:"{deck_name}"')
    for note_id in added_note_ids:
        assert note_id not in note_ids


def test_add_notes_to_anki_mocked(mock_anki_connect):
    mock_anki_connect.return_value.side_effect = [
        {'permission': 'granted'},  # requestPermission
        [{'name': 'Default', 'id': 1}],  # deckNames
        [{'name': 'Basic', 'id': 2}],  # modelNames
        {'result': 101},  # addNote for first note
        {'result': 102}  # addNote for second note
    ]

    notes = [{'sentence': 'This is a test sentence', 'word': 'test'}]
    deck_name = 'Test Deck'
    model_name = 'Basic Model'

    result = ankikindle.add_notes_to_anki(notes, deck_name, model_name, anki_connect=mock_anki_connect)
    assert result == [101, 102]
