import logging
import threading
import ankiconnect_wrapper
import vocab_db_accessor_wrap
from datetime import datetime
from sqlite3 import Connection


logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s')
ankikindle_main_logger = logging.getLogger(__name__)

PRIORITY_DECK_NAME = 'Priority Deck'
MAX_EXAMPLE_SENTENCES = 3
# TODO figure out a good practice here: how could this be implemented to work for first time users in general
#  initial ideas:
#  ア）provide config allowing for an initial timestamp to designate where the user wants to try to generate cards
#  イ）just initially target all ALL vocab highlights they've made up until using the app


DEFAULT_TIMESTAMP = vocab_db_accessor_wrap.get_timestamp_ms(2023, 4, 28)

_running = False


def main(connection_injection: Connection, ankiconnect_injection: ankiconnect_wrapper, stop_event: threading.Event):
    global _running
    _running = True
    try:
        while not stop_event.is_set():
            process_new_vocab_highlights(connection_injection, ankiconnect_injection)

    except ConnectionError as e:
        ankikindle_main_logger.error(f"connection error occurred during ankikindle run{e}")
    finally:
        _running = False


def process_new_vocab_highlights(connection_injection: Connection, ankiconnect_injection: ankiconnect_wrapper) -> list[dict]:
    latest_timestamp = vocab_db_accessor_wrap.get_latest_timestamp(connection_injection)
    if latest_timestamp is None:
        latest_timestamp = DEFAULT_TIMESTAMP
        ankikindle_main_logger.info(f"latest timestamp not found in the timestamp table, initializing to default: {latest_timestamp}")
        vocab_db_accessor_wrap.set_latest_timestamp(connection_injection, latest_timestamp)
    vocab_highlights = vocab_db_accessor_wrap.get_word_lookups_after_timestamp(connection_injection, latest_timestamp)
    if vocab_highlights:
        ankikindle_main_logger.info(f"new vocab_highlights:{vocab_highlights} were found")
        add_notes_to_anki(vocab_highlights, deck_name="mail_sucks_in_japan", card_type="aedict",  # TODO fix this to use custom deck
                          ankiconnect_injection=ankiconnect_injection)
        latest_timestamp = vocab_db_accessor_wrap.get_latest_lookup_timestamp(connection_injection)
        vocab_db_accessor_wrap.set_latest_timestamp(connection_injection, latest_timestamp)
        ankikindle_main_logger.info(f"latest_timestamp is now :{datetime.fromtimestamp(latest_timestamp / 1000)}")
    return vocab_highlights


# ANKI STUFF
def add_notes_to_anki(vocab_highlights: list[dict], deck_name: str, card_type: str,
                      ankiconnect_injection: ankiconnect_wrapper) -> list[int]:
    ankikindle_main_logger.info("Adding notes to Anki...")
    try:
        ankiconnect_request_permission(ankiconnect_injection)
        if deck_name not in ankiconnect_injection.get_all_deck_names():
            raise ValueError(f"Deck named: '{deck_name}' was not found in local Anki account")
        if card_type not in ankiconnect_injection.get_all_card_type_names():
            raise ValueError(f"Card type: '{card_type}' was not found in local Anki account")
        added_note_ids = []
        for index, vocab_highlight in enumerate(vocab_highlights):
            note_id = add_or_update_note(vocab_highlight, deck_name, card_type, ankiconnect_injection)
            added_note_ids.append(note_id)
            ankikindle_main_logger.info(f"Added note {index + 1}/{len(vocab_highlights)}: {vocab_highlight['word']} (Note ID: {note_id})")

        ankikindle_main_logger.info(f"Successfully added {len(added_note_ids)} notes to Anki.")
        return added_note_ids
    except ValueError as e:
        ankikindle_main_logger.error(f"ValueError: {e}")
    except ConnectionError as e:
        ankikindle_main_logger.error(f"ConnectionError: {e}")
    except Exception as e:
        ankikindle_main_logger.error(f"Unexpected error: {e}")


def add_or_update_note(word_highlight: dict, deck_name: str, card_type: str,
                       ankiconnect_injection: ankiconnect_wrapper) -> int:
    existing_note_id = find_existing_note_id(word_highlight['word'], deck_name, ankiconnect_injection)
    if existing_note_id > 0:  # -1 id means note doesn't exist
        ankikindle_main_logger.info(
            f"note already exists for '{word_highlight['word']}' in '{deck_name}' deck; thus updating that note")
        update_note_with_more_examples(existing_note_id, word_highlight['usage'], ankiconnect_injection)
        ankikindle_main_logger.info(f"note updated successfully")
        return existing_note_id
    else:
        ankikindle_main_logger.info(
            f"no existing note found for '{word_highlight['word']}' in '{deck_name}' deck; thus adding new note")
        return add_new_note(word_highlight, deck_name, card_type, ankiconnect_injection)


def find_existing_note_id(word: str, deck_name: str, ankiconnect_injection: ankiconnect_wrapper) -> int:
    query = f"deck:'{deck_name}' 'Furigana:{word}'"
    return ankiconnect_injection.get_anki_note_id_from_query(query)


def update_note_with_more_examples(note_id: int, new_example: str, ankiconnect_injection: ankiconnect_wrapper):
    ankikindle_main_logger.info(f"Updating note with ID {note_id} by adding new example: '{new_example}'")

    note = ankiconnect_injection.get_single_anki_note_details(note_id, True)
    note_fields = note['fields']
    example_sentences = note_fields['Sentence']

    updated_example_sentences = _update_example_sentences(example_sentences, new_example)
    note_fields['Sentence'] = updated_example_sentences
    ankikindle_main_logger.debug(f"Updated example sentences: '{updated_example_sentences}'")

    containing_decks = ankiconnect_injection.get_decks_containing_card(note_id)
    if PRIORITY_DECK_NAME not in containing_decks:
        current_tags = note['tags']
        counter_tag = int(current_tags[0]) if not current_tags else 1  # assume only one tag? maybe use a field later?
        counter_tag += 1
        if counter_tag >= 3:
            note['deckName'] = PRIORITY_DECK_NAME  # TODO this wont work, u hav to upd8 the note deck differently
            ankikindle_main_logger.info(f"Note with ID {note_id} now belongs to the '{PRIORITY_DECK_NAME}' deck")
        ankiconnect_injection.update_anki_note(note_id, note_fields, counter_tag)
        ankikindle_main_logger.info(f"Note with ID {note_id} updated successfully")


def _update_example_sentences(example_sentences: str, new_example: str) -> str:
    example_sentence_list = example_sentences.split('</br>')
    example_sentence_list.insert(0, new_example)
    if len(example_sentence_list) > MAX_EXAMPLE_SENTENCES:
        example_sentence_list.pop()
    example_sentences = '</br>'.join(example_sentence_list)
    return example_sentences


def add_new_note(word_highlight: dict, deck_name: str, card_type: str,
                 ankiconnect_injection: ankiconnect_wrapper) -> int:
    fields = {
        'Expression': word_highlight['usage'],
        'Furigana': word_highlight['word'],
        'Sentence': word_highlight['usage']
    }
    anki_note = {'deckName': deck_name, 'modelName': card_type, 'tags': ['1'], 'fields': fields}
    return ankiconnect_injection.add_anki_note(anki_note)


def ankiconnect_request_permission(ankiconnect_injection: ankiconnect_wrapper):
    result = ankiconnect_injection.request_connection_permission()
    if not result['permission'] == 'granted':
        raise ConnectionError(f"failed to authenticate with anki; response: {result}")


# TODO only for recovery during unmocked connection testing purposes (adding unwanted cards). move somewhere else or
#  figure out it being needed later
def remove_notes_from_anki(note_id_to_be_deleted: int, ankiconnect_injection: ankiconnect_wrapper):
    ankikindle_main_logger.info(f"removing cards...")
    ankiconnect_request_permission(ankiconnect_injection)
    ankiconnect_injection.delete_anki_note(note_id_to_be_deleted)
    ankikindle_main_logger.info(f"Note with ID {note_id_to_be_deleted} has been removed successfully")

