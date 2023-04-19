import ankisync2
import pytest

import ankiconnect_wrapper
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
    ankiconnect_wrapper_mock = Mock()
    ankiconnect_wrapper_mock.request_connection_permission.return_value = {'permission': 'denied'}
    with pytest.raises(Exception) as e:
        ankikindle.ankiconnect_request_permission(ankiconnect_wrapper_mock)
    assert str(e.value) == "Failed to authenticate with Anki; response: {'permission': 'denied'}"


def test_add_notes_to_anki_mocked_no_duplicate_found():
    ankiconnect_wrapper_mock = Mock()
    ankiconnect_wrapper_mock.request_connection_permission.return_value = {'permission': 'granted'}
    ankiconnect_wrapper_mock.get_all_deck_names.return_value = ['Default']
    ankiconnect_wrapper_mock.get_all_card_type_names.return_value = ['Basic']
    ankiconnect_wrapper_mock.get_anki_note_ids_from_query.return_value = []
    ankiconnect_wrapper_mock.add_anki_note.return_value = 101

    notes = [{'sentence': 'This is a test sentence', 'word': 'test'}]
    deck_name = 'Default'
    model_name = 'Basic'

    result_note_ids = ankikindle.add_notes_to_anki(notes, deck_name, model_name, ankiconnect_wrapper_mock)
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
        [{'Default': [1]}],  # getDecks
        None,  # updateNoteFields
        None
    ]
    ankikindle.update_note_with_more_examples(101, 'example2', mock_anki_connect)
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
    # TODO fix this to be the actual input for updateNoteFields, since input param is messed up value order thing (
    #  look into insomnia)
    # mock_anki_connect.assert_any_call('updateNoteFields', note=expected_note)


def test_add_update_and_remove_notes_to_anki():
    deck_name = 'mail sucks in japan'
    model_name = 'aedict'
    notes = [
        {'sentence': '若槻は狐につままれたような面持ちで確認した。', 'word': '狐につままれ'}
    ]
    added_note_ids = ankikindle.add_notes_to_anki(notes, deck_name, model_name, ankiconnect_wrapper)

    all_note_ids = ankisync2.ankiconnect(ankikindle.FIND_NOTES, query=f'deck:"{deck_name}"')
    for note_id in added_note_ids:
        assert note_id in all_note_ids

    new_example = '狐につままれの新しい例文'
    ankikindle.update_note_with_more_examples(added_note_ids[0], new_example, ankisync2.ankiconnect)

    updated_note = ankisync2.ankiconnect('notesInfo', notes=[added_note_ids[0]])[0]
    assert new_example in updated_note['fields'][ankikindle.EXAMPLE_SENTENCE]['value']
    assert updated_note['tags'][0] == '2'

    ankikindle.remove_notes_from_anki(added_note_ids, ankisync2.ankiconnect)
    note_ids = ankisync2.ankiconnect(ankikindle.FIND_NOTES, query=f"deck:'{deck_name}'")
    for note_id in added_note_ids:
        assert note_id not in note_ids
