from flask import jsonify, request
from app.routes import anki_routes
from app.services.anki_service import AnkiService

def handle_service_response(response):
    if 'error' in response:
        return jsonify({"success": False, "message": response['error']}), 500
    return jsonify({"success": True, "data": response}), 200

@anki_routes.route('/request_permission', methods=['GET'])
def request_permission():
    response = AnkiService.request_connection_permission()
    return handle_service_response(response)

@anki_routes.route('/decks', methods=['GET'])
def get_decks():
    response = AnkiService.get_all_deck_names()
    return handle_service_response(response)

@anki_routes.route('/models', methods=['GET'])
def get_models():
    response = AnkiService.get_all_model_names()
    return handle_service_response(response)

@anki_routes.route('/find_notes', methods=['POST'])
def find_notes():
    query = request.json.get('query', '')
    response = AnkiService.find_notes(query)
    return handle_service_response(response)

@anki_routes.route('/note_info', methods=['POST'])
def get_notes_info():
    note_ids = request.json.get('note_ids', [])
    response = AnkiService.get_notes_info(note_ids)
    return handle_service_response(response)

@anki_routes.route('/add_note', methods=['POST'])
def add_note():
    data = request.json
    response = AnkiService.add_anki_note(
        deck_name=data['deck_name'],
        model_name=data['model_name'],
        front=data['front'],
        back=data['back'],
        tags=data.get('tags', [])
    )
    return handle_service_response({"note_id": response} if response else {"error": "Failed to add note"})

@anki_routes.route('/update_note', methods=['POST'])
def update_note():
    data = request.json
    note_id = data.get('note_id')
    fields = data.get('fields', {})
    if not note_id or not fields:
        return jsonify({"success": False, "message": "Note ID and fields are required"}), 400
    response = AnkiService.update_note_fields(note_id, fields)
    return handle_service_response(response)
