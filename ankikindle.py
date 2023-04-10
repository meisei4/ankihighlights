import logging
import requests
import ankisync2.ankiconnect

# Replace <YOUR_AUTHORIZATION_HEADER> with the value you copied from the "Authorization" header in the developer tools.
logger = logging.getLogger(__name__)

#TODO come up with good names for stuff like note, clipping, card, word, expressions and etc

def main():
    deck_name, model_name = get_deck_and_model_names()

    # TODO get header and actually have this response thing work
    headers = ""
    response = requests.get(f'https://kindle.amazon.com/kp/kindle-dbs/notes/2010-05-01/<YOUR_TITLE>',
                            headers=headers)
    clippings_json = response.json()
    clippings = parse_clippings(clippings_json)
    for clipping in clippings:
        anki_notes = build_notes(clipping['notes'])
        add_notes_to_anki(anki_notes, deck_name, model_name)


def get_deck_and_model_names():
    deck_name = input("Enter the name of the deck you want to add notes to: ")
    model_name = input("Enter the name of the note type you want to use: ")
    return deck_name, model_name


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


def add_notes_to_anki(cards, deck_name, model_name):
    ankiconnect_request_permission()
    confirm_existence_of_ankiconnect_item_by_name('deckNames', deck_name)
    confirm_existence_of_ankiconnect_item_by_name('modelNames', model_name)
    added_note_ids = []
    for card in cards:
        fields = {
            'Expression': card['sentence'],
            'Furigana': card['word']
        }
        note = {'deckName': deck_name, 'modelName': model_name, 'fields': fields}
        result = ankisync2.ankiconnect('addNote', note=note)
        added_note_ids.append(result)
    return added_note_ids


def ankiconnect_request_permission():
    anki_conn = ankisync2.ankiconnect('requestPermission')
    if not anki_conn['permission'] == 'granted':
        raise Exception(f"Failed to authenticate with Anki; response: {anki_conn}")


def confirm_existence_of_ankiconnect_item_by_name(action, target_item):
    items = ankisync2.ankiconnect(f'{action}')
    if target_item not in items:
        raise Exception(f"{action.capitalize()} '{target_item}' not found in remote Anki account")
    return True


def remove_notes_from_anki(added_note_ids):
    ankiconnect_request_permission()
    notes_to_delete = ankisync2.ankiconnect('findNotes', query=f"nid:{','.join(str(n) for n in added_note_ids)}")
    ankisync2.ankiconnect('deleteNotes', notes=notes_to_delete)
