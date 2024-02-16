import time
import typing
import logging
import requests


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8765/"
GLOB_HEADERS = {"Content-Type": "application/json"}
VERSION = 6


def log_request_info(response, action, elapsed_time=None):
    status_code = response.status_code
    response_text = response.text
    if elapsed_time is not None:
        logger.info(f"AnkiConnect: {action} request elapsed time: {elapsed_time:.3f}s")
    logger.info(f"AnkiConnect: {action} request status code: {status_code}")
    logger.info(f"AnkiConnect: {action} request response: {response_text}")


def request_connection_permission() -> str:
    payload = {
        "action": "requestPermission",
        "version": VERSION
    }
    start_time = time.time()
    response = requests.get(API_URL, json=payload, headers=GLOB_HEADERS)
    elapsed_time = time.time() - start_time
    log_request_info(response, "requestPermission", elapsed_time)
    return response.json()["result"]


def get_all_deck_names() -> list[str]:
    payload = {
        "action": "deckNames",
        "version": VERSION
    }
    start_time = time.time()
    response = requests.get(API_URL, json=payload, headers=GLOB_HEADERS)
    elapsed_time = time.time() - start_time
    log_request_info(response, "deckNames", elapsed_time)
    return response.json()["result"]


def get_all_card_type_names() -> list[str]:
    payload = {
        "action": "modelNames",
        "version": VERSION
    }
    start_time = time.time()
    response = requests.get(API_URL, json=payload, headers=GLOB_HEADERS)
    elapsed_time = time.time() - start_time
    log_request_info(response, "modelNames", elapsed_time)
    return response.json()["result"]


def get_decks_containing_card(card_id: int) -> list[str]:
    payload = {
        "action": "getDecks",
        "version": VERSION,
        "params": {
            "cards": [card_id]
        }
    }
    start_time = time.time()
    response = requests.get(API_URL, json=payload, headers=GLOB_HEADERS)
    elapsed_time = time.time() - start_time
    log_request_info(response, "getDecks", elapsed_time)
    return response.json()["result"].keys()


def get_anki_card_ids_from_query(query: str) -> list[int]:
    payload = {
        "action": "findCards",
        "version": VERSION,
        "params": {"query": query}
    }
    start_time = time.time()
    response = requests.get(API_URL, json=payload, headers=GLOB_HEADERS)
    elapsed_time = time.time() - start_time
    log_request_info(response, "findCards", elapsed_time)
    return response.json()["result"]


def get_anki_note_ids_from_query(query: str) -> list[int]:
    payload = {
        "action": "findNotes",
        "version": VERSION,
        "params": {"query": query}
    }
    start_time = time.time()
    response = requests.get(API_URL, json=payload, headers=GLOB_HEADERS)
    elapsed_time = time.time() - start_time
    log_request_info(response, "findNotes", elapsed_time)
    return response.json()["result"]


def get_anki_note_id_from_query(query: str) -> typing.Optional:
    note_ids = get_anki_note_ids_from_query(query)
    if note_ids:
        return note_ids[0]
    else:
        return -1


def get_anki_cards_details(list_of_card_ids: list[int], order_boolean: bool) -> list[dict]:
    payload = {
        "action": "cardsInfo",
        "version": VERSION,
        "params": {"cards": list_of_card_ids}
    }
    start_time = time.time()
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)
    elapsed_time = time.time() - start_time
    response_json = response.json()["result"]
    if order_boolean:
        response_json = remove_value_order_from_dict(response_json)
    log_request_info(response, "cardsInfo", elapsed_time)
    return response_json


def get_single_anki_card_details(card_id: int, remove_order_boolean: bool) -> dict:
    response = get_anki_cards_details([card_id], remove_order_boolean)
    return response[0]


def get_anki_notes_details(list_of_note_ids: list[int], remove_order_boolean: bool) -> list[dict]:
    payload = {
        "action": "notesInfo",
        "version": VERSION,
        "params": {"notes": list_of_note_ids}
    }
    start_time = time.time()
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)
    elapsed_time = time.time() - start_time
    response_json = response.json()["result"]
    if remove_order_boolean:
        response_json = remove_value_order_from_dict(response_json)
    log_request_info(response, "notesInfo", elapsed_time)
    return response_json


def get_single_anki_note_details(note_id: int, remove_order_boolean: bool) -> dict:
    response = get_anki_notes_details([note_id], remove_order_boolean)
    return response[0]


def add_anki_note(note: dict) -> int:
    payload = {
        "action": "addNote",
        "version": VERSION,
        "params": {
            "note": note
        }
    }
    start_time = time.time()
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)
    elapsed_time = time.time() - start_time
    log_request_info(response, "addNote", elapsed_time)
    return response.json()["result"]


def delete_anki_note(note_id: int):
    payload = {
        "action": "deleteNotes",
        "version": VERSION,
        "params": {
            "notes": [note_id]
        }
    }
    start_time = time.time()
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)
    elapsed_time = time.time() - start_time
    log_request_info(response, "deleteNotes", elapsed_time)


def update_anki_note(note_id: int, fields: dict, tag: int) -> None:
    payload = {
        "action": "updateNoteFields",
        "version": VERSION,
        "params": {
            "note": {
                "id": note_id,
                "fields": fields
            }
        }
    }
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)
    log_request_info(response, "updateNoteFields")
    payload = {
        "action": "replaceTags",
        "version": VERSION,
        "params": {
            "notes": [note_id],
            "tag_to_replace": str(tag - 1),  # TODO ugly way to do this, but updateTags doesn't seem to work
            "replace_with_tag": str(tag)
        }
    }
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)
    log_request_info(response, "replaceTags")


def get_anki_note_from_card(card_id: int) -> int:
    payload = {
        "action": "cardsInfo",
        "version": VERSION,
        "params": {"cards": [card_id]}
    }
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS).json()["result"]
    note_id = response[0]["noteId"]
    return note_id


def add_new_deck_to_anki(deck_name: str) -> int:
    payload = {
        "action": "createDeck",
        "version": VERSION,
        "params": {
            "deck": deck_name
        }
    }
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)
    log_request_info(response, "createDeck")
    deck_id = response.json()["result"]
    return deck_id


def add_new_card_type_to_anki(card_type_name: str, fields: list[str], templates: list[dict], css: str = "") -> None:
    payload = {
        "action": "createModel",
        "version": VERSION,
        "params": {
            "modelName": card_type_name,
            "inOrderFields": fields,
            "css": css,
            "cardTemplates": templates
        }
    }
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)
    log_request_info(response, "createModel")


# AUXILIARIES
def remove_value_order_from_dict(result: list[dict]) -> list[dict]:
    updated_result = result
    for i in range(len(result)):
        fields_keys = result[i]["fields"].keys()
        for field_key in fields_keys:
            updated_result[i]["fields"][field_key] = result[i]["fields"][field_key]["value"]
    return updated_result
