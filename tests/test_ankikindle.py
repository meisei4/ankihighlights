import sqlite3
import time
import pytest
import threading
import ankiconnect_wrapper
import vocab_db_accessor_wrap
from .. import ankikindle
from sqlite3 import Connection
from unittest.mock import Mock
from . import test_vocab_database_wrapper


# TODO this test module and the test_vocab_database_wrapper test module crossover here so fix that
@pytest.fixture(scope='module')
def test_db_connection():
    with sqlite3.connect(test_vocab_database_wrapper.TEST_VOCAB_DB_FILE) as conn:
        yield conn
        test_vocab_database_wrapper.cleanup_test_data(conn)


def test_update_database_while_main_program_is_running(test_db_connection: Connection):
    ankikindle_mock = Mock()
    # Create a flag to signal when the database update has been processed
    db_updated_flag = threading.Event()

    # TODO this is only updating the db and then causing the main loop in ankikindle to be stopped (doesnt get to see the update)
    db_update_thread = threading.Thread(target=test_vocab_database_wrapper.simulate_db_update, args=(db_updated_flag, ))

    db_update_thread.start()
    # Define the target function and its arguments for the main thread
    ankikindle.run_ankikindle(test_vocab_database_wrapper.TEST_VOCAB_DB_FILE, test_db_connection, ankikindle_mock, db_updated_flag)

    # Wait for the database update thread to finish updating the database
    db_updated_flag.wait()
    db_update_thread.join()

    expected_highlights = [
        {"word": "example", "sentence": "This is the first example sentence."},
        {"word": "example", "sentence": "This is the second example sentence."}
    ]
    test_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2023, 4, 28)
    result = vocab_db_accessor_wrap.get_all_word_look_ups_after_timestamp(test_db_connection, test_timestamp)

    assert len(result) == 1
    assert result[0]["word"] == "日本語"
    assert result[0]["usage"] == "日本語の例文"
    assert result[0]["title"] == "日本の本"
    assert result[0]["authors"] == "著者A"

    # TODO assert that the anki cards were made?


def test_ankiconnect_request_permission_permission_denied():
    ankiconnect_wrapper_mock = Mock()
    ankiconnect_wrapper_mock.request_connection_permission.return_value = {'permission': 'denied'}
    with pytest.raises(Exception) as e:
        ankikindle.ankiconnect_request_permission(ankiconnect_wrapper_mock)
    assert str(e.value) == "failed to authenticate with anki; response: {'permission': 'denied'}"


def test_add_notes_to_anki_mocked_no_duplicate_found():
    ankiconnect_wrapper_mock = Mock()
    ankiconnect_wrapper_mock.request_connection_permission.return_value = {'permission': 'granted'}
    ankiconnect_wrapper_mock.get_all_deck_names.return_value = ['Default']
    ankiconnect_wrapper_mock.get_all_card_type_names.return_value = ['Basic']
    ankiconnect_wrapper_mock.get_anki_note_id_from_query.return_value = -1
    ankiconnect_wrapper_mock.add_anki_note.return_value = 101

    word_highlights = [{'usage': 'This is a test sentence', 'word': 'test'}]
    deck_name = 'Default'
    model_name = 'Basic'

    result_note_ids = ankikindle.add_notes_to_anki(word_highlights, deck_name, model_name, ankiconnect_wrapper_mock)
    assert result_note_ids == [101]


def test_update_note_with_more_examples_mocked():
    ankiconnect_wrapper_mock = Mock()
    mocked_return_value = {'noteId': 101,
                           'modelName': 'Basic',
                           'deckName': 'Default',
                           'tags': ['1'],
                           'fields': {
                               'Furigana': 'test',
                               'Expression': 'This is a test sentence',
                               'Sentence': 'example1',
                               'Meaning': '',
                               'Pronunciation': ''
                           }
                           }  # notesInfo for first note
    ankiconnect_wrapper_mock.get_single_anki_note_details.return_value = mocked_return_value
    ankiconnect_wrapper_mock.get_decks_containing_card.return_value = ['Default']
    ankiconnect_wrapper_mock.update_anki_note.return_value = None
    ankikindle.update_note_with_more_examples(101, 'example2', ankiconnect_wrapper_mock)

    expected_fields = {
        'Furigana': 'test',
        'Expression': 'This is a test sentence',
        'Sentence': 'example2' + '</br>' + 'example1',
        'Meaning': '',
        'Pronunciation': ''
    }
    ankiconnect_wrapper_mock.update_anki_note.assert_called_once_with(101, expected_fields, 2)


def test_update_example_sentences():
    example_sentences = ''
    new_example = 'Example 1.'
    expected_output = 'Example 1.</br>'
    assert ankikindle._update_example_sentences(example_sentences, new_example) == expected_output

    example_sentences = 'Example 2.</br>Example 1.'
    new_example = 'Example 3.'
    expected_output = 'Example 3.</br>Example 2.</br>Example 1.'
    assert ankikindle._update_example_sentences(example_sentences, new_example) == expected_output

    example_sentences = 'Example 3.</br>Example 2.</br>Example 1.'
    new_example = 'Example 4.'
    expected_output = 'Example 4.</br>Example 3.</br>Example 2.'
    assert ankikindle._update_example_sentences(example_sentences, new_example) == expected_output


def test_add_update_and_remove_notes_to_anki():
    deck_name = 'mail_sucks_in_japan'
    model_name = 'aedict'
    notes = [
        {'usage': '若槻は狐につままれたような面持ちで確認した。', 'word': '狐につままれ'}
    ]
    added_note_ids = ankikindle.add_notes_to_anki(notes, deck_name, model_name, ankiconnect_wrapper)

    all_note_ids_of_deck_that_was_added_to = ankiconnect_wrapper.get_anki_note_ids_from_query(f'deck:{deck_name}')
    for note_id in added_note_ids:
        assert note_id in all_note_ids_of_deck_that_was_added_to

    new_example = '狐につままれの新しい例文'
    note_to_be_updated = added_note_ids[0]
    ankikindle.update_note_with_more_examples(note_to_be_updated, new_example, ankiconnect_wrapper)

    updated_note = ankiconnect_wrapper.get_single_anki_note_details(note_to_be_updated, True)
    assert new_example in updated_note['fields']['Sentence']
    assert updated_note['tags'][0] == '2'

    added_and_updated_note_id = updated_note['noteId']
    ankikindle.remove_notes_from_anki(updated_note['noteId'], ankiconnect_wrapper)
    note_ids_after_deletion = ankiconnect_wrapper.get_anki_note_ids_from_query(f'deck:"{deck_name}"')
    assert added_and_updated_note_id not in note_ids_after_deletion
