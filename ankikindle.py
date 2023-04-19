import logging
import requests
import ankisync2.ankiconnect

import ankiconnect_wrapper

# ankiconnect actions
ADD_NOTE = 'addNote'
DELETE_NOTES = 'deleteNotes'
# TODO figure out how findNotes return type looks
FIND_NOTES = 'findNotes'
DECK_NAMES = 'deckNames'
MODEL_NAMES = 'modelNames'

# dict keys
EXAMPLE_SENTENCE = 'Sentence'
NOTES = 'notes'
SENTENCE = 'sentence'
WORD = 'word'

# Replace <YOUR_AUTHORIZATION_HEADER> with the value you copied from the 'Authorization' header in the developer tools.
logger = logging.getLogger(__name__)


def main(anki_connect_injection):
    deck_name = ''
    model_name = ''

    # TODO get header and actually have this response thing work
    headers = ""
    response = requests.get(f'https://kindle.amazon.com/kp/kindle-dbs/notes/2010-05-01/<YOUR_TITLE>', headers=headers)
    clippings_json = response.json()
    clippings = parse_clippings(clippings_json)
    for clipping in clippings:
        anki_notes = build_notes(clipping[NOTES])
        add_notes_to_anki(anki_notes, deck_name, model_name, anki_connect_injection)


def parse_clippings(clippings_json):
    clippings = []
    for clipping in clippings_json:
        clippings.append({
            'asin': clipping['asin'],
            'lastUpdatedDate': clipping['lastUpdatedDate'],
            'authors': clipping['authors'],
            'title': clipping['title'],
            NOTES: clipping[NOTES]
        })
    return clippings


def build_notes(notes_dict):
    anki_notes = []
    for note in notes_dict:
        anki_note = build_single_note(note)
        anki_notes.append(anki_note)
    return anki_notes


def build_single_note(note_contents):
    sentence = note_contents[SENTENCE]
    word = note_contents['highlight']
    return {SENTENCE: sentence, WORD: word}


def add_notes_to_anki(clipping_notes, deck_name, model_name, ankiconnect_injection):
    ankiconnect_request_permission(ankiconnect_injection)
    if deck_name not in ankiconnect_injection.get_all_deck_names():
        raise Exception(f"'{deck_name}' not found in remote Anki account")
    if model_name not in ankiconnect_injection.get_all_card_type_names():
        raise Exception(f"'{model_name}' not found in remote Anki account")
    added_note_ids = []
    for clipping_note in clipping_notes:
        note_id = add_or_update_note(clipping_note, deck_name, model_name, ankiconnect_injection)
        added_note_ids.append(note_id)
    return added_note_ids


def add_or_update_note(clipping_note, deck_name, model_name, anki_connect_injection):
    query = 'deck:"{}" "Furigana:{}"'.format(deck_name, clipping_note[WORD])
    existing_notes = ankiconnect_wrapper.get_anki_note_ids_from_query(query)
    if len(existing_notes) >= 1:
        update_note_with_more_examples(existing_notes[0], clipping_note[SENTENCE], anki_connect_injection)
        return existing_notes[0]
    return add_new_note(clipping_note, deck_name, model_name, anki_connect_injection)


def update_note_with_more_examples(note_id, new_example, anki_connect_injection):
    new_note = anki_connect_injection('notesInfo', notes=[note_id])[0]
    new_fields = new_note['fields']
    more_examples = new_fields[EXAMPLE_SENTENCE]['value']
    # TODO check here for how many occurrences of \n (or </br>) there are, and only allow 2 max (for 3 example
    #  sentences). otherwise replace the oldest sentence with the new_example
    more_examples += '</br>' + new_example
    # TODO replace all of the Command based stuff with the new ankiconnect_wrapper
    new_fields['Sentence'] = more_examples  # ew
    new_fields['Expression'] = new_fields['Expression']['value']  # ew
    new_fields['Furigana'] = new_fields['Furigana']['value']  # ew
    new_fields['Meaning'] = new_fields['Meaning']['value']  # ew
    new_fields['Pronunciation'] = new_fields['Pronunciation']['value']  # ew

    current_deck = anki_connect_injection('getDecks', cards=[note_id])  # ew notes and cards bleh
    if 'Priority Words' not in current_deck:
        previous_tags = new_note['tags']
        # 'not tags' means its empty??
        counter_tag = int(previous_tags[0]) if not previous_tags else 1  # assume only one tag? maybe use a field later.
        counter_tag += 1
        if counter_tag >= 3:
            new_note['deckName'] = 'Priority Words'
        anki_connect_injection('updateNoteFields', note={'id': note_id, 'fields': new_fields})
        # TODO this takes a while... so maybe figure out a better way to update the whole note at once
        # anki_connect_injection('updateNoteTags', note=note_id, tags=[str(counter_tag)])
        anki_connect_injection('replaceTags', notes=[note_id], tag_to_replace=previous_tags[0],
                               replace_with_tag=str(counter_tag))
    else:
        anki_connect_injection('updateNoteFields', note={'id': note_id, 'fields': new_fields})


def add_new_note(clipping_note, deck_name, model_name, anki_connect_injection):
    fields = {
        'Expression': clipping_note[SENTENCE],
        'Furigana': clipping_note[WORD],
        EXAMPLE_SENTENCE: clipping_note[SENTENCE],  # still keep the front of the card visible if needed (especially
        # when more sentences start to overwrite this somehow)
    }
    anki_note = {'deckName': deck_name, 'modelName': model_name, 'tags': ['1'], 'fields': fields}
    return anki_connect_injection.add_anki_note(anki_note)


def ankiconnect_request_permission(ankiconnect_wrapper_injection):
    result = ankiconnect_wrapper_injection.request_connection_permission()
    if not result['permission'] == 'granted':
        raise Exception(f'Failed to authenticate with Anki; response: {result}')


# TODO only for recovery during unmocked connection testing purposes (adding unwanted cards). move somewhere else or
#  figure out it being needed later
def remove_notes_from_anki(note_ids_to_be_removed, anki_connect_injection):
    ankiconnect_request_permission(anki_connect_injection)
    notes_to_delete = ankisync2.ankiconnect(FIND_NOTES,
                                            query=f"nid:{','.join(str(n) for n in note_ids_to_be_removed)}")
    ankisync2.ankiconnect(DELETE_NOTES, notes=notes_to_delete)
