from flask import Blueprint, jsonify
from app.services.ankiconnect_service import AnkiService
from app.services.vocab_highlight_service import VocabHighlightService

vocab_highlight_routes = Blueprint('vocab_highlights', __name__, url_prefix='/vocab_highlights')

@vocab_highlight_routes.route('/process', methods=['POST'])
def process_highlights():
    try:
        VocabHighlightService.process_highlights()
        return jsonify({"success": True, "message": "Vocab highlights processed successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@vocab_highlight_routes.route('/request_permission', methods=['POST'])
def request_permission():
    try:
        result = AnkiService.request_connection_permission()
        return jsonify({"success": True, "result": result}), 200 if result else 403
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# You can add more routes here for specific functionalities like fetching individual highlights, updating, or deleting.

