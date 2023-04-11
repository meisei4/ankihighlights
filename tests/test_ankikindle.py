import ankisync2
import pytest

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


def test_update_note_with_more_examples(mock_anki_connect_injection):
    mock_anki_connect = Mock()
    mock_anki_connect.side_effect = [
        {'permission': 'granted'},  # requestPermission
        ['Default'],  # deckNames
        ['Basic'],  # modelNames
        [101],  # found note
        101,  # addNote for first note
    ]

    notes = [{'sentence': 'This is a test sentence', 'word': 'test'}]
    deck_name = 'Default'
    model_name = 'Basic'

    ankikindle.update_note_with_more_examples(1, 'example2', mock_anki_connect_injection)

    # Check that anki_connect_injection was called with the expected arguments
    mock_anki_connect_injection.assert_called_once_with('notesInfo', notes=[1])
    expected_note = {'Example Sentence': 'example1<br/>example2'}
    mock_anki_connect_injection.assert_any_call('updateNoteFields', note=expected_note)
    # TODO have an assert here


# TODO remove this test because unit test probably shouldn't touch the actual anki API
#  this is just the first test to actually confirm it works
def test_add_and_remove_notes_to_anki():
    deck_name = 'mail sucks in japan'
    model_name = 'aedict'
    notes = [
        {'sentence': '若槻は狐につままれたような面持ちで確認した。', 'word': '狐につままれ'}
    ]
    added_note_ids = ankikindle.add_notes_to_anki(notes, deck_name, model_name, ankisync2.ankiconnect)

    all_note_ids = ankisync2.ankiconnect(ankikindle.FIND_NOTES, query=f"deck:'{deck_name}'")
    for note_id in added_note_ids:
        assert note_id in all_note_ids

    ankikindle.remove_notes_from_anki(added_note_ids, ankisync2.ankiconnect)

    note_ids = ankisync2.ankiconnect(ankikindle.FIND_NOTES, query=f"deck:'{deck_name}'")
    for note_id in added_note_ids:
        assert note_id not in note_ids
