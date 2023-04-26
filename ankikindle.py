import logging
from typing import List

import ankiconnect_wrapper

logger = logging.getLogger(__name__)

PRIORITY_DECK_NAME = 'Priority Deck'
MAX_EXAMPLE_SENTENCES = 3


def parse_clippings(clippings_json: List[dict]) -> List[dict]:
    clippings = []
    for clipping in clippings_json:
        clippings.append({
            'asin': clipping['asin'],
            'lastUpdatedDate': clipping['lastUpdatedDate'],
            'authors': clipping['authors'],
            'title': clipping['title'],
            'notes': clipping['notes']
        })
    return clippings


def build_notes(notes_dict: List[dict]) -> List[dict]:
    return [build_single_note(note) for note in notes_dict]


def build_single_note(note_contents: dict) -> dict:
    sentence = note_contents['sentence']
    word = note_contents['highlight']
    return {'sentence': sentence, 'word': word}


def add_notes_to_anki(clipping_notes: List[dict], deck_name: str, card_type: str, ankiconnect_injection: ankiconnect_wrapper) -> List[int]:
    logger.info("Adding notes to Anki...")
    try:
        ankiconnect_request_permission(ankiconnect_injection)
        if deck_name not in ankiconnect_injection.get_all_deck_names():
            raise ValueError(f"'{deck_name}' not found in remote Anki account")
        if card_type not in ankiconnect_injection.get_all_card_type_names():
            raise ValueError(f"'{card_type}' not found in remote Anki account")
        added_note_ids = []
        for clipping_note in clipping_notes:
            note_id = add_or_update_note(clipping_note, deck_name, card_type, ankiconnect_injection)
            added_note_ids.append(note_id)
        logger.info(f"Added {len(added_note_ids)} notes successfully.")
        return added_note_ids
    except ValueError as e:
        logger.error(f"ValueError: {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


def add_or_update_note(clipping_note: dict, deck_name: str, card_type: str, ankiconnect_injection: ankiconnect_wrapper) -> int:
    existing_note_id = find_existing_note_id(clipping_note['word'], deck_name, ankiconnect_injection)
    if existing_note_id:
        update_note_with_more_examples(existing_note_id, clipping_note['sentence'], ankiconnect_injection)
        return existing_note_id
    else:
        return add_new_note(clipping_note, deck_name, card_type, ankiconnect_injection)


def find_existing_note_id(word: str, deck_name: str, ankiconnect_injection: ankiconnect_wrapper) -> int:
    query = f"deck:'{deck_name}' 'Furigana:{word}'"
    return ankiconnect_injection.get_anki_note_id_from_query(query)


def update_note_with_more_examples(note_id: int, new_example: str, ankiconnect_injection: ankiconnect_wrapper):
    note = ankiconnect_injection.get_single_anki_note_details(note_id, True)
    note_fields = note['fields']
    example_sentences = note_fields['Sentence']
    example_sentences = _check_and_update_example_sentences(example_sentences, new_example)
    note_fields['Sentence'] = example_sentences
    # TODO figure out if this works with cards, sometimes cards and notes have different ids
    containing_decks = ankiconnect_injection.get_decks_containing_card(note_id)
    if PRIORITY_DECK_NAME not in containing_decks:
        current_tags = note['tags']
        counter_tag = int(current_tags[0]) if not current_tags else 1  # assume only one tag? maybe use a field later?
        counter_tag += 1
        if counter_tag >= 3:
            note['deckName'] = PRIORITY_DECK_NAME  # TODO this wont work, u hav to upd8 the note deck differently
        ankiconnect_injection.update_anki_note(note_id, note_fields, str(counter_tag))


def _check_and_update_example_sentences(example_sentences: str, new_example: str) -> str:
    example_sentence_list = example_sentences.split('</br>')
    example_sentence_list.insert(0, new_example)
    if len(example_sentence_list) > MAX_EXAMPLE_SENTENCES:
        example_sentence_list.pop()
    example_sentences = '</br>'.join(example_sentence_list)
    return example_sentences


def add_new_note(clipping_note: dict, deck_name: str, card_type: str, ankiconnect_injection: ankiconnect_wrapper) -> int:
    fields = {
        'Expression': clipping_note['sentence'],
        'Furigana': clipping_note['word'],
        'Sentence': clipping_note['sentence']
    }
    anki_note = {'deckName': deck_name, 'modelName': card_type, 'tags': ['1'], 'fields': fields}
    return ankiconnect_injection.add_anki_note(anki_note)


def ankiconnect_request_permission(ankiconnect_injection: ankiconnect_wrapper):
    result = ankiconnect_injection.request_connection_permission()
    if not result['permission'] == 'granted':
        raise ConnectionError(f'Failed to authenticate with Anki; response: {result}')


# TODO only for recovery during unmocked connection testing purposes (adding unwanted cards). move somewhere else or
#  figure out it being needed later
def remove_notes_from_anki(note_id_to_be_deleted: int, ankiconnect_injection: ankiconnect_wrapper):
    ankiconnect_request_permission(ankiconnect_injection)
    ankiconnect_injection.delete_anki_note(note_id_to_be_deleted)
