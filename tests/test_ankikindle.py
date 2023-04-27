import sqlite3
import threading
import time
from sqlite3 import Connection

import pytest
import ankiconnect_wrapper
import vocab_db_accessor_wrap
from . import test_vocab_database_wrapper
from .. import ankikindle
from unittest.mock import Mock


@pytest.fixture(scope='module')
def test_db_connection():
    with sqlite3.connect(test_vocab_database_wrapper.TEST_VOCAB_DB_FILE) as conn:
        yield conn
        test_vocab_database_wrapper.cleanup_test_data(conn)


def simulate_db_update(test_db_connection: Connection):
    test_timestamp = vocab_db_accessor_wrap.get_timestamp_ms(2030, 4, 25)
    with test_db_connection as test_db_connection:
        cursor = test_db_connection.cursor()
        cursor.execute("BEGIN")
        cursor.execute(f"""
                    INSERT INTO WORDS (id, word, stem, lang, category, timestamp, profileid) 
                    VALUES ('1234', '日本語', '日本', 'ja', 1, {test_timestamp}, 'test')
                """)
        cursor.execute("""
                    INSERT INTO BOOK_INFO (id, asin, guid, lang, title, authors) 
                    VALUES ('1234', 'B123', 'G456', 'ja', '日本の本', '著者A')
                """)
        cursor.execute(f"""
                    INSERT INTO LOOKUPS (id, word_key, book_key, dict_key, pos, usage, timestamp) 
                    VALUES ('1351', '1234', '1234', '1', 'n', '日本語の例文', {test_timestamp})
                """)
        cursor.execute("END")


def thread_testing_thing():
    ankikindle_mock = Mock()
    vocab_db_accessor_wrap_mock = Mock()
    thread = threading.Thread(target=ankikindle.do_the_thing_a_spike_lee_joint)
    thread.start()

    # wait for the function to start running before updating the database file
    time.sleep(1)

    simulate_db_update()

    thread.join()
    assert vocab_db_accessor_wrap_mock.copy_vocab_db_to_backup_and_tmp_upon_proper_access.call_count == 2
    assert ankikindle_mock.add_notes_to_anki.call_count == 2

    expected_highlights = [
        {"word": "example", "sentence": "This is the first example sentence."},
        {"word": "example", "sentence": "This is the second example sentence."}
    ]
    ankikindle_mock.add_or_update_note.assert_called_once_with(expected_highlights[0], any, any, any)
    ankikindle_mock.add_or_update_note.assert_called_once_with(expected_highlights[1], any, any, any)
    assert vocab_db_accessor_wrap_mock.get_latest_lookup_timestamp.call_count == 2


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
