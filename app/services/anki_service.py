import os
import requests
from app.app import logger


class AnkiService:
    API_URL = os.getenv("API_URL")
    HEADERS = {"Content-Type": "application/json"}
    VERSION = 6  # Defaulting to 6 as a safe fallback

    @classmethod
    def send_request(cls, action, params=None) -> dict:
        payload = {"action": action, "version": cls.VERSION, "params": params or {}}
        try:
            response = requests.post(cls.API_URL, json=payload, headers=cls.HEADERS)
            response_data = response.json()
            logger.info(f"AnkiConnect {action}: {response_data}")
            return response_data
        except requests.RequestException as e:
            logger.error(f"AnkiConnect {action} error: {e}")
            return {"error": str(e)}

    @classmethod
    def request_connection_permission(cls):
        return cls.send_request("requestPermission")

    @classmethod
    def get_all_deck_names(cls):
        return cls.send_request("deckNames").get("result", [])

    @classmethod
    def get_all_model_names(cls):
        return cls.send_request("modelNames").get("result", [])

    @classmethod
    def find_notes(cls, query):
        return cls.send_request("findNotes", {"query": query}).get("result", [])

    @classmethod
    def get_notes_info(cls, note_ids):
        return cls.send_request("notesInfo", {"notes": note_ids}).get("result", [])

    @classmethod
    def add_anki_note(cls, deck_name, model_name, front, back, tags=None):
        note = {
            "deckName": deck_name,
            "modelName": model_name,
            "fields": {"Front": front, "Back": back},
            "tags": tags or [],
        }
        return cls.send_request("addNote", {"note": note}).get("result")

    @classmethod
    def update_note_fields(cls, note_id, fields):
        note = {"id": note_id, "fields": fields}
        return cls.send_request("updateNoteFields", {"note": note}).get("result")
