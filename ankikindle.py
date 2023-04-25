import logging
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import ankiconnect_wrapper

# Replace <YOUR_AUTHORIZATION_HEADER> with the value you copied from the 'Authorization' header in the developer tools.
logger = logging.getLogger(__name__)


def main(ankiconnect_injection):
    deck_name = ''
    model_name = ''

    # TODO implement scraper here to get clippings
    clippings = []
    for clipping in clippings:
        anki_notes = build_notes(clipping['notes'])
        add_notes_to_anki(anki_notes, deck_name, model_name, ankiconnect_injection)


def connect_to_clippings():
    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')  # Run Firefox in headless mode, without opening a window
    driver = webdriver.Firefox(options=options)
    driver.get("https://read.amazon.co.jp/")

    email_field = driver.find_element(By.ID, "ap_email")
    email_field.send_keys("your_email@example.com")

    password_field = driver.find_element(By.ID, "ap_password")
    password_field.send_keys("your_password")

    signin_button = driver.find_element(By.ID, "signInSubmit")
    signin_button.click()

    library_div = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "kp-notebook-library")))

    book_elements = library_div.find_elements(By.CLASS_NAME, "kp-notebook-library-each-book")

    for book_element in book_elements:
        title_element = book_element.find_element(By.CLASS_NAME, "kp-notebook-library-each-book-title")
        print(title_element.text)


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


def add_or_update_note(clipping_note, deck_name, model_name, ankiconnect_injection: ankiconnect_wrapper):
    query = f"deck:'{deck_name}' 'Furigana:{clipping_note['word']}'"
    # TODO this should only ever return length 1, so why even have it return an array
    existing_notes = ankiconnect_injection.get_anki_note_ids_from_query(query)
    if len(existing_notes) >= 1:
        update_note_with_more_examples(existing_notes[0], clipping_note['sentence'], ankiconnect_injection)
        return existing_notes[0]
    return add_new_note(clipping_note, deck_name, model_name, ankiconnect_injection)


def update_note_with_more_examples(note_id, new_example, ankiconnect_injection: ankiconnect_wrapper):
    note = ankiconnect_injection.get_single_anki_note_details(note_id, True)
    new_fields = note['fields']
    more_examples = new_fields['Sentence']
    more_examples = _check_and_update_example_sentences(more_examples, new_example)
    new_fields['Sentence'] = more_examples
    # TODO figure out if this works with cards, sometimes cards and notes have different ids
    containing_decks = ankiconnect_injection.get_decks_containing_card(note_id)
    if 'Priority Words' not in containing_decks:
        previous_tags = note['tags']
        counter_tag = int(previous_tags[0]) if not previous_tags else 1  # assume only one tag? maybe use a field later.
        counter_tag += 1
        if counter_tag >= 3:
            note['deckName'] = 'Priority Words'  # TODO this wont work, u hav to upd8 the note deck differently
        ankiconnect_injection.update_anki_note(note_id, new_fields, str(counter_tag))


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
        'Sentence': clipping_note['sentence'],  # still keep the front of the card visible if needed (especially
        # when more sentences start to overwrite this somehow)
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
