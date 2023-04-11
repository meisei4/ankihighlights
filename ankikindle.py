import logging
import requests
import ankisync2.ankiconnect

# Replace <YOUR_AUTHORIZATION_HEADER> with the value you copied from the "Authorization" header in the developer tools.
logger = logging.getLogger(__name__)

# TODO come up with good names for stuff like note, clipping, card, word, expressions etc later


def main(anki_connect_injection):
    deck_name = ""
    model_name = ""

    # TODO get header and actually have this response thing work
    headers = ""
    response = requests.get(f'https://kindle.amazon.com/kp/kindle-dbs/notes/2010-05-01/<YOUR_TITLE>', headers=headers)
    clippings_json = response.json()
    clippings = parse_clippings(clippings_json)
    for clipping in clippings:
        anki_notes = build_notes(clipping['notes'])
        add_notes_to_anki(anki_notes, deck_name, model_name, anki_connect_injection)


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
        anki_note = build_note(note)
        anki_notes.append(anki_note)
    return anki_notes


def build_note(note_contents):
    sentence = note_contents['sentence']
    word = note_contents['highlight']
    return {'sentence': sentence, 'word': word}


def add_notes_to_anki(clipping_notes, deck_name, model_name, anki_connect_injection):
    ankiconnect_request_permission(anki_connect_injection)
    confirm_existence_of_ankiconnect_item_by_name('deckNames', deck_name, anki_connect_injection)
    confirm_existence_of_ankiconnect_item_by_name('modelNames', model_name, anki_connect_injection)
    added_note_ids = []
    for clipping_note in clipping_notes:
        fields = {
            'Expression': clipping_note['sentence'],
            'Furigana': clipping_note['word']
        }
        anki_note = {'deckName': deck_name, 'modelName': model_name, 'fields': fields}
        result = anki_connect_injection('addNote', note=anki_note)
        # TODO check for dupes?
        added_note_ids.append(result)
    return added_note_ids


def ankiconnect_request_permission(anki_connect_injection):
    anki_conn = anki_connect_injection('requestPermission')
    if not anki_conn['permission'] == 'granted':
        raise Exception(f"Failed to authenticate with Anki; response: {anki_conn}")


def confirm_existence_of_ankiconnect_item_by_name(action, target_item, anki_connect_injection):
    items = anki_connect_injection(f'{action}')
    if target_item not in items:
        raise Exception(f"{action.capitalize()} '{target_item}' not found in remote Anki account")
    return True


def remove_notes_from_anki(added_note_ids, anki_connect_injection):
    ankiconnect_request_permission(anki_connect_injection)
    notes_to_delete = ankisync2.ankiconnect('findNotes', query=f"nid:{','.join(str(n) for n in added_note_ids)}")
    ankisync2.ankiconnect('deleteNotes', notes=notes_to_delete)
