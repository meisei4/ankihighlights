import requests

api_url = "http://localhost:8765/"  # maybe this can be updated in the future
glob_headers = {"Content-Type": "application/json"}
version = 6


def request_connection_permission():
    payload = {
        "action": "requestPermission",
        "version": version
    }
    response = requests.request("GET", api_url, json=payload, headers=glob_headers)
    return response.json()["result"]


def get_all_deck_names():
    payload = {
        "action": "deckNames",
        "version": version
    }
    response = requests.request("GET", api_url, json=payload, headers=glob_headers)
    return response.json()["result"]


def get_all_card_type_names():
    payload = {
        "action": "modelNames",
        "version": version
    }
    response = requests.request("GET", api_url, json=payload, headers=glob_headers)
    return response.json()["result"]


def get_anki_card_ids_from_query(query):
    payload = {
        "action": "findCards",
        "version": version,
        "params": {"query": query}
    }
    response = requests.request("GET", api_url, json=payload, headers=glob_headers)
    return response.json()["result"]


# TODO now have to replace a lot of the card vs note api thing...
def remove_value_order_from_dict(result):
    updated_result = result
    for i in range(len(result)):
        fields_keys = result[i]["fields"].keys()
        for field_key in fields_keys:
            updated_result[i]["fields"][field_key] = result[i]["fields"][field_key]["value"]
    return updated_result


def get_anki_cards_details(array_of_card_ids, order_boolean):
    payload = {
        "action": "cardsInfo",
        "version": version,
        "params": {"cards": array_of_card_ids}
    }
    result = requests.request("GET", api_url, json=payload, headers=glob_headers).json()["result"]
    if order_boolean:
        return remove_value_order_from_dict(result)
    return result


def get_single_anki_card_details(card_id, remove_order_boolean):
    payload = {
        "action": "cardsInfo",
        "version": version,
        "params": {"cards": [card_id]}
    }
    result = requests.request("GET", api_url, json=payload, headers=glob_headers).json()["result"][0]
    if remove_order_boolean:
        return remove_value_order_from_dict(result)
    return result


def get_anki_note_ids_from_query(query):
    payload = {
        "action": "findNotes",
        "version": version,
        "params": {"query": query}
    }
    response = requests.request("GET", api_url, json=payload, headers=glob_headers)
    return response.json()["result"]


def get_anki_note_details(array_of_note_ids, remove_order_boolean):
    payload = {
        "action": "notesInfo",
        "version": version,
        "params": {"cards": array_of_note_ids}
    }
    result = requests.request("GET", api_url, json=payload, headers=glob_headers).json()["result"][0]
    if remove_order_boolean:
        return remove_value_order_from_dict(result)
    return result


def add_anki_note(note):
    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": note
        }
    }
    response = requests.request("GET", api_url, json=payload, headers=glob_headers)
    return response.json()["result"]
