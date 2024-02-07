from flask import Blueprint, jsonify, request

from app.services.ankiconnect_service import AnkiService

anki_routes = Blueprint('anki', __name__, url_prefix='/anki')

@anki_routes.route('/request_permission', methods=['GET'])
def request_permission():
    try:
        permission_granted = AnkiService.request_connection_permission()
        return jsonify({"success": True, "permission_granted": permission_granted}), 200 if permission_granted else 403
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@anki_routes.route('/decks', methods=['GET'])
def get_decks():
    try:
        decks = AnkiService.get_all_deck_names()
        return jsonify({"success": True, "decks": decks}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@anki_routes.route('/models', methods=['GET'])
def get_models():
    try:
        models = AnkiService.get_all_model_names()
        return jsonify({"success": True, "models": models}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@anki_routes.route('/find_notes', methods=['POST'])
def find_notes():
    try:
        query = request.json.get('query', '')
        notes = AnkiService.find_notes(query)
        return jsonify({"success": True, "notes": notes}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@anki_routes.route('/note_info', methods=['POST'])
def get_notes_info():
    try:
        note_ids = request.json.get('note_ids', [])
        notes_info = AnkiService.get_notes_info(note_ids)
        return jsonify({"success": True, "notes_info": notes_info}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@anki_routes.route('/add_note', methods=['POST'])
def add_note():
    try:
        data = request.json
        note_id = AnkiService.add_anki_note(
            deck_name=data['deck_name'],
            model_name=data['model_name'],
            front=data['front'],
            back=data['back'],
            tags=data.get('tags', [])
        )
        if note_id:
            return jsonify({"success": True, "note_id": note_id}), 200
        else:
            return jsonify({"success": False, "message": "Failed to add note"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Add more routes as necessary for your application's functionality, like updating or deleting notes.
