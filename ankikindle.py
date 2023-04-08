import logging
import requests
import ankisync2.ankiconnect

# Replace <YOUR_AUTHORIZATION_HEADER> with the value you copied from the "Authorization" header in the developer tools.
logger = logging.getLogger(__name__)


def main():
    username, password = get_login_credentials()

    deck_name, model_name = get_deck_and_model_names()

    # TODO get header and actually have this response thing work
    headers = ""
    response = requests.get(f'https://kindle.amazon.com/kp/kindle-dbs/notes/2010-05-01/<YOUR_TITLE>',
                            headers=headers)
    clippings_json = response.json()
    clippings = parse_clippings(clippings_json)
    for clipping in clippings:
        anki_cards = parse_notes(clipping['notes'])
        add_cards_to_anki(anki_cards, deck_name, model_name, username, password)


def get_login_credentials():
    username = input("Enter your Anki username: ")
    password = input("Enter your Anki password: ")
    return username, password


def get_deck_and_model_names():
    deck_name = input("Enter the name of the deck you want to add cards to: ")
    model_name = input("Enter the name of the card type you want to use: ")
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


def parse_notes(notes):
    anki_cards = []
    for note in notes:
        card = build_card_from_note(note)
        anki_cards.append(card)
    return anki_cards


def build_card_from_note(note):
    sentence = note['sentence']
    word = note['highlight']
    return {'sentence': sentence, 'word': word}


def add_cards_to_anki(cards, deck_name, model_name):
    connection = ankisync2.ankiconnect('requestPermission')
    if not connection['result']:
        raise Exception(f"Failed to authenticate with Anki: {connection['error']}")

    deck = next((d for d in connection.deckList() if d['name'] == deck_name), None)
    if not deck:
        raise Exception(f"Deck '{deck_name}' not found in remote Anki account")
    models = connection.modelList()
    model = next((m for m in models if m['name'] == model_name), None)
    if not model:
        raise Exception(f"Model '{model_name}' not found in remote Anki account")

    added_note_ids = []
    for card in cards:
        fields = {
            'Expression': card['sentence'],
            'Furigana': card['word']
        }
        note = {'deckName': deck_name, 'modelName': model_name, 'fields': fields, 'tags': ['kindle']}
        result = connection.invoke('addNote', note=note)
        added_note_ids.append(result['result'])

    connection.disconnect()
    return added_note_ids


def remove_cards_from_anki(added_note_ids):
    connection = ankisync2.ankiconnect('requestPermission')
    if not connection['result']:
        raise Exception(f"Failed to authenticate with Anki: {connection['error']}")

    notes_to_delete = connection.invoke('findNotes', query=f"nid:{','.join(added_note_ids)}")
    connection.invoke('deleteNotes', notes=notes_to_delete)

    connection.disconnect()
