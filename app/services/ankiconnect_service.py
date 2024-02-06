import requests
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class AnkiService:
    API_URL = "http://localhost:8765"
    HEADERS = {"Content-Type": "application/json"}
    VERSION = 6

    @staticmethod
    def log_request_info(response, action):
        logger.info(f"AnkiConnect: {action} request status code: {response.status_code}")
        logger.info(f"AnkiConnect: {action} request response: {response.text}")

    @staticmethod
    def request_connection_permission() -> bool:
        payload = {"action": "requestPermission", "version": AnkiService.VERSION}
        response = requests.post(AnkiService.API_URL, json=payload, headers=AnkiService.HEADERS)
        AnkiService.log_request_info(response, "requestPermission")
        return response.json().get("result", False)

    @staticmethod
    def get_all_deck_names() -> List[str]:
        payload = {"action": "deckNames", "version": AnkiService.VERSION}
        response = requests.post(AnkiService.API_URL, json=payload, headers=AnkiService.HEADERS)
        AnkiService.log_request_info(response, "deckNames")
        return response.json().get("result", [])

    @staticmethod
    def get_all_model_names() -> List[str]:
        payload = {"action": "modelNames", "version": AnkiService.VERSION}
        response = requests.post(AnkiService.API_URL, json=payload, headers=AnkiService.HEADERS)
        AnkiService.log_request_info(response, "modelNames")
        return response.json().get("result", [])

    @staticmethod
    def find_notes(query: str) -> List[int]:
        payload = {"action": "findNotes", "version": AnkiService.VERSION, "params": {"query": query}}
        response = requests.post(AnkiService.API_URL, json=payload, headers=AnkiService.HEADERS)
        AnkiService.log_request_info(response, "findNotes")
        return response.json().get("result", [])

    @staticmethod
    def get_notes_info(note_ids: List[int]) -> List[Dict]:
        payload = {"action": "notesInfo", "version": AnkiService.VERSION, "params": {"notes": note_ids}}
        response = requests.post(AnkiService.API_URL, json=payload, headers=AnkiService.HEADERS)
        AnkiService.log_request_info(response, "notesInfo")
        return response.json().get("result", [])

    @staticmethod
    def add_anki_note(deck_name: str, model_name: str, front: str, back: str, tags: Optional[List[str]] = None) -> Optional[int]:
        payload = {
            "action": "addNote",
            "version": AnkiService.VERSION,
            "params": {
                "note": {
                    "deckName": deck_name,
                    "modelName": model_name,
                    "fields": {"Front": front, "Back": back},
                    "tags": tags or [],
                }
            }
        }
        response = requests.post(AnkiService.API_URL, json=payload, headers=AnkiService.HEADERS)
        AnkiService.log_request_info(response, "addNote")
        return response.json().get("result")

    @staticmethod
    def update_note_fields(note_id: int, fields: Dict[str, str]) -> None:
        payload = {
            "action": "updateNoteFields",
            "version": AnkiService.VERSION,
            "params": {
                "note": {
                    "id": note_id,
                    "fields": fields,
                }
            }
        }
        response = requests.post(AnkiService.API_URL, json=payload, headers=AnkiService.HEADERS)
        AnkiService.log_request_info(response, "updateNoteFields")

    # Add more methods as needed for full functionality.

    # Example for deleting notes, getting card info, etc., can be added following the same pattern.
