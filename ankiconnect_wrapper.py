import requests

api_url = "http://localhost:8765/"  # maybe this can be updated in the future
glob_headers = {"Content-Type": "application/json"}
version = 6


def get_all_deck_names():
    payload = {
        "action": "deckNames",
        "version": version
    }
    response = requests.request("GET", api_url, json=payload, headers=glob_headers)
    return response


def get_all_card_type_names():
    payload = {
        "action": "modelNames",
        "version": version
    }
    response = requests.request("GET", api_url, json=payload, headers=glob_headers)
    return response


def get_anki_card_ids_from_query(query):
    payload = {
        "action": "findCards",
        "version": version,
        "params": {"query": query}
    }
    response = requests.request("GET", api_url, json=payload, headers=glob_headers)
    return response


def get_anki_card_details(array_of_card_ids):
    payload = {
        "action": "cardsInfo",
        "version": version,
        "params": {"cards": array_of_card_ids}
    }
    response = requests.request("GET", api_url, json=payload, headers=glob_headers)
    return response


def get_anki_note_ids_from_query(query):
    payload = {
        "action": "findNotes",
        "version": version,
        "params": {"query": query}
    }
    response = requests.request("GET", api_url, json=payload, headers=glob_headers)
    return response


def get_anki_note_details(array_of_note_ids):
    payload = {
        "action": "notesInfo",
        "version": version,
        "params": {"cards": array_of_note_ids}
    }
    response = requests.request("GET", api_url, json=payload, headers=glob_headers)
    return response

