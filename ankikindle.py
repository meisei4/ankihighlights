import logging
import ankiconnect_wrapper

logger = logging.getLogger(__name__)


def parse_clippings(clippings_json):
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


def build_notes(notes_dict):
    anki_notes = []
    for note in notes_dict:
        anki_note = build_single_note(note)
        anki_notes.append(anki_note)
    return anki_notes


def build_single_note(note_contents):
    sentence = note_contents['sentence']
    word = note_contents['highlight']
    return {'sentence': sentence, 'word': word}


def add_notes_to_anki(clipping_notes, deck_name, model_name, ankiconnect_injection: ankiconnect_wrapper):
    logger.info("Adding notes to Anki...")
    try:
        ankiconnect_request_permission(ankiconnect_injection)
        if deck_name not in ankiconnect_injection.get_all_deck_names():
            raise ValueError(f"'{deck_name}' not found in remote Anki account")
        if model_name not in ankiconnect_injection.get_all_card_type_names():
            raise ValueError(f"'{model_name}' not found in remote Anki account")
        added_note_ids = []
        for clipping_note in clipping_notes:
            note_id = add_or_update_note(clipping_note, deck_name, model_name, ankiconnect_injection)
            added_note_ids.append(note_id)
        logger.info("Added notes successfully.")
        return added_note_ids
    except ValueError as e:
        logger.error(f"ValueError: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


def add_or_update_note(clipping_note, deck_name, model_name, ankiconnect_injection: ankiconnect_wrapper):
    query = f"deck:'{deck_name}' 'Furigana:{clipping_note['word']}'"
    note = ankiconnect_injection.get_anki_note_id_from_query(query)
    if not note:
        return add_new_note(clipping_note, deck_name, model_name, ankiconnect_injection)
    update_note_with_more_examples(note, clipping_note['sentence'], ankiconnect_injection)
    return note


def update_note_with_more_examples(note_id, new_example, ankiconnect_injection: ankiconnect_wrapper):
    note = ankiconnect_injection.get_single_anki_note_details(note_id, True)
    note_fields = note['fields']
    example_sentences = note_fields['Sentence']
    example_sentences = _check_and_update_example_sentences(example_sentences, new_example)
    note_fields['Sentence'] = example_sentences
    # TODO figure out if this works with cards, sometimes cards and notes have different ids
    containing_decks = ankiconnect_injection.get_decks_containing_card(note_id)
    if 'Priority Words' not in containing_decks:
        current_tags = note['tags']
        counter_tag = int(current_tags[0]) if not current_tags else 1  # assume only one tag? maybe use a field later?
        counter_tag += 1
        if counter_tag >= 3:
            note['deckName'] = 'Priority Words'  # TODO this wont work, u hav to upd8 the note deck differently
        ankiconnect_injection.update_anki_note(note_id, note_fields, str(counter_tag))


def _check_and_update_example_sentences(more_examples, new_example):
    example_list = more_examples.split('</br>')
    example_list.insert(0, new_example)
    if len(example_list) > 3:
        example_list.pop()
    more_examples = '</br>'.join(example_list)
    return more_examples


def add_new_note(clipping_note, deck_name, model_name, ankiconnect_injection: ankiconnect_wrapper):
    fields = {
        'Expression': clipping_note['sentence'],
        'Furigana': clipping_note['word'],
        'Sentence': clipping_note['sentence']
    }
    anki_note = {'deckName': deck_name, 'modelName': model_name, 'tags': ['1'], 'fields': fields}
    return ankiconnect_injection.add_anki_note(anki_note)


def ankiconnect_request_permission(ankiconnect_injection):
    result = ankiconnect_injection.request_connection_permission()
    if not result['permission'] == 'granted':
        raise Exception(f'Failed to authenticate with Anki; response: {result}')


# TODO only for recovery during unmocked connection testing purposes (adding unwanted cards). move somewhere else or
#  figure out it being needed later
def remove_notes_from_anki(note_id_to_be_deleted, ankiconnect_injection: ankiconnect_wrapper):
    ankiconnect_request_permission(ankiconnect_injection)
    ankiconnect_injection.delete_anki_note(note_id_to_be_deleted)
