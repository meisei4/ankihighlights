import json

import ankisync2
import pytest
import requests

from .. import ankikindle
from unittest.mock import Mock


def test_build_notes():
    notes = [{'annotationId': 'ABCDEFGH1234',
              'highlight': '狐につままれ',
              'location': {'value': 4, 'type': 'page'},
              'sentence': '若槻は狐につままれたような面持ちで確認した。',
              'note': ''}]
    expected_notes = [{'sentence': '若槻は狐につままれたような面持ちで確認した。', 'word': '狐につままれ'}]
    assert ankikindle.build_notes(notes) == expected_notes


def test_ankiconnect_request_permission_permission_denied():
    mock_anki_connect_injection = Mock(return_value={'permission': 'denied'})
    with pytest.raises(Exception) as e:
        ankikindle.ankiconnect_request_permission(mock_anki_connect_injection)
    assert str(e.value) == "Failed to authenticate with Anki; response: {'permission': 'denied'}"
    mock_anki_connect_injection.assert_called_once_with('requestPermission')


def test_confirm_existence_of_ankiconnect_item_by_name_no_items_found():
    mock_anki_connect_injection = Mock(return_value=[])
    with pytest.raises(Exception) as e:
        ankikindle.confirm_existence_of_ankiconnect_item_by_name('getItems', 'test_item', mock_anki_connect_injection)
    assert str(e.value) == "getItems 'test_item' not found in remote Anki account"
    mock_anki_connect_injection.assert_called_once_with('getItems')


def test_add_notes_to_anki_mocked_no_duplicate_found():
    mock_anki_connect = Mock()
    mock_anki_connect.side_effect = [
        {'permission': 'granted'},  # requestPermission
        ['Default'],  # deckNames
        ['Basic'],  # modelNames
        [],
        101,  # addNote for first note
    ]

    notes = [{'sentence': 'This is a test sentence', 'word': 'test'}]
    deck_name = 'Default'
    model_name = 'Basic'

    result_note_ids = ankikindle.add_notes_to_anki(notes, deck_name, model_name,
                                                   anki_connect_injection=mock_anki_connect)
    assert result_note_ids == [101]


def test_update_note_with_more_examples_mocked():
    mock_anki_connect = Mock()
    mock_anki_connect.side_effect = [
        [{
            'noteId': 101,
            'modelName': 'Basic',
            'deckName': 'Default',
            'tags': ['1'],
            'fields': {
                'Furigana': {'value': 'test', 'order': 0},
                'Expression': {'value': 'example1', 'order': 1},
                'Sentence': {'value': 'example1', 'order': 2},
                'Meaning': {'value': '', 'order': -1},
                'Pronunciation': {'value': '', 'order': -1}
            }
        }],  # notesInfo for first note
        [{'Default': [1]}], # getDecks
        None  # updateNoteFields
    ]
    ankikindle.update_note_with_more_examples(101, 'example2', mock_anki_connect)
    # TODO notesInfo is insane it has a ton of value and order info in the dict.
    #  figure out how to get around this easier
    mock_anki_connect.assert_any_call('notesInfo', notes=[101])
    expected_note = {
        'id': 101,
        'tags': ['2'],
        'fields': {
            'Furigana': {'value': 'test', 'order': 0},
            'Expression': {'value': 'This is a test sentence', 'order': 1},
            'Sentence': {'value': 'example1' + '\n' + 'example2', 'order': 2},
            'Meaning': {'value': '', 'order': -1},
            'Pronunciation': {'value': '', 'order': -1}
        }
    }
    # this is not this input for the actual updateNoteFields, since input param is messed up value order thing
    # mock_anki_connect.assert_any_call('updateNoteFields', note=expected_note)


# TODO remove this test because unit test probably shouldn't touch the actual anki API
#  this is just the first test to actually confirm it works
def test_add_and_remove_notes_to_anki():
    deck_name = 'mail sucks in japan'
    model_name = 'aedict'
    notes = [
        {'sentence': '若槻は狐につままれたような面持ちで確認した。', 'word': '狐につままれ'}
    ]
    added_note_ids = ankikindle.add_notes_to_anki(notes, deck_name, model_name, ankisync2.ankiconnect)

    all_note_ids = ankisync2.ankiconnect(ankikindle.FIND_NOTES, query=f'deck:"{deck_name}"')
    for note_id in added_note_ids:
        assert note_id in all_note_ids

    ankikindle.remove_notes_from_anki(added_note_ids, ankisync2.ankiconnect)

    note_ids = ankisync2.ankiconnect(ankikindle.FIND_NOTES, query=f"deck:'{deck_name}'")
    for note_id in added_note_ids:
        assert note_id not in note_ids


def test_add_update_and_remove_notes_to_anki():
    deck_name = 'mail sucks in japan'
    model_name = 'aedict'
    notes = [
        {'sentence': '若槻は狐につままれたような面持ちで確認した。', 'word': '狐につままれ'}
    ]
    added_note_ids = ankikindle.add_notes_to_anki(notes, deck_name, model_name, ankisync2.ankiconnect)

    # test that added notes are in the deck
    all_note_ids = ankisync2.ankiconnect(ankikindle.FIND_NOTES, query=f'deck:"{deck_name}"')
    for note_id in added_note_ids:
        assert note_id in all_note_ids

    # update the first note
    new_example = '狐につままれの新しい例文'
    ankikindle.update_note_with_more_examples(added_note_ids[0], new_example, ankisync2.ankiconnect)

    updated_note = ankisync2.ankiconnect('notesInfo', notes=[added_note_ids[0]])[0]
    assert new_example in updated_note['fields'][ankikindle.EXAMPLE_SENTENCE]['value']

    # remove the added notes
    ankikindle.remove_notes_from_anki(added_note_ids, ankisync2.ankiconnect)
    # TODO this is not actually the correct note ids, i think that the updateNotes will update the note_id so you need
    #  to get the new ones id
    note_ids = ankisync2.ankiconnect(ankikindle.FIND_NOTES, query=f"deck:'{deck_name}'")
    for note_id in added_note_ids:
        assert note_id not in note_ids
