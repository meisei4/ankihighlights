import typing

import requests

API_URL = "http://localhost:8765/"  # maybe this can be updated in the future
GLOB_HEADERS = {"Content-Type": "application/json"}
VERSION = 6


def request_connection_permission() -> str:
    payload = {
        "action": "requestPermission",
        "version": VERSION
    }
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)
    return response.json()["result"]


def get_all_deck_names() -> list[str]:
    payload = {
        "action": "deckNames",
        "version": VERSION
    }
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)
    return response.json()["result"]


def get_all_card_type_names() -> list[str]:
    payload = {
        "action": "modelNames",
        "version": VERSION
    }
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)
    return response.json()["result"]


def get_decks_containing_card(card_id: int) -> list[str]:
    payload = {
        "action": "getDecks",
        "version": VERSION,
        "params": {
            "cards": [card_id]
        }
    }
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)
    return response.json()["result"].keys()


def get_anki_card_ids_from_query(query: str) -> list[int]:
    payload = {
        "action": "findCards",
        "version": VERSION,
        "params": {"query": query}
    }
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)
    return response.json()["result"]


def get_anki_note_ids_from_query(query: str) -> list[int]:
    payload = {
        "action": "findNotes",
        "version": VERSION,
        "params": {"query": query}
    }
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)
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
    result = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS).json()["result"]
    if order_boolean:
        return remove_value_order_from_dict(result)
    return result


def get_single_anki_card_details(card_id: int, remove_order_boolean: bool) -> dict:
    return get_anki_cards_details([card_id], remove_order_boolean)[0]


def get_anki_notes_details(list_of_note_ids: list[int], remove_order_boolean: bool) -> list[dict]:
    payload = {
        "action": "notesInfo",
        "version": VERSION,
        "params": {"notes": list_of_note_ids}
    }
    result = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS).json()["result"]
    if remove_order_boolean:
        return remove_value_order_from_dict(result)
    return result


def get_single_anki_note_details(note_id: int, remove_order_boolean: bool) -> dict:
    return get_anki_notes_details([note_id], remove_order_boolean)[0]


def add_anki_note(note: dict) -> int:
    payload = {
        "action": "addNote",
        "version": VERSION,
        "params": {
            "note": note
        }
    }
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)
    return response.json()["result"]


def delete_anki_note(note_id: int):
    payload = {
        "action": "deleteNotes",
        "version": VERSION,
        "params": {
            "notes": [note_id]
        }
    }
    requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)


def update_anki_note(note_id: int, fields: dict, tag: int):
    payload_for_fields = {
        "action": "updateNoteFields",
        "version": VERSION,
        "params": {
            "note": {
                "id": note_id,
                "fields": fields
            }
        }
    }
    requests.request("GET", API_URL, json=payload_for_fields, headers=GLOB_HEADERS)
    payload_for_tag = {
        "action": "replaceTags",
        "version": VERSION,
        "params": {
            "notes": [note_id],
            "tag_to_replace": str(tag - 1),  # TODO ugly way to do this, but updateTags doesn't seem to work
            "replace_with_tag": str(tag)
        }
    }
    requests.request("GET", API_URL, json=payload_for_tag, headers=GLOB_HEADERS)


def get_anki_note_from_card(card_id: int) -> int:
    payload = {
        "action": "cardsToNotes",
        "version": VERSION,
        "params": {
            "cards": [card_id]
        }
    }
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)
    return response.json()["result"][0]


# TODO figure this out, when trying to add a new card just create new deck if the user doesnt want to decide a deck name
def add_new_deck_to_anki(deck_name: str):
    payload = {
        "action": "createDeck",
        "version": VERSION,
        "params": {
            "deck": deck_name
        }
    }
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)
    return response.json()["result"]


# TODO figure this out (gonna have to create a specific card type at a some point,
#  but remember to make it as customizable as possible according to anyone who will fork this project
def add_new_card_type_to_anki(card_type_name: str):
    payload = {
        "action": "createModel",
        "version": VERSION,
        "params": {
            "modelName": card_type_name,
            "inOrderFields": ["Field1", "Field2", "Field3"],
            "css": "Optional CSS with default to builtin css", # ????
            "isCloze": False, #????
            "cardTemplates": [
                {
                    "Name": "My Card 1",
                    "Front": "Front html {{Field1}}",
                    "Back": "Back html  {{Field2}}"
                }
            ]
        }
    }
    response = requests.request("GET", API_URL, json=payload, headers=GLOB_HEADERS)
    return response.json()["result"]


# AUXILIARIES
def remove_value_order_from_dict(result: list[dict]) -> list[dict]:
    updated_result = result
    for i in range(len(result)):
        fields_keys = result[i]["fields"].keys()
        for field_key in fields_keys:
            updated_result[i]["fields"][field_key] = result[i]["fields"][field_key]["value"]
    return updated_result
