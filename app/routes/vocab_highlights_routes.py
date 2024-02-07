from flask import Blueprint, jsonify, request
from app.services.ankiconnect_service import AnkiService
from app.services.vocab_highlight_service import VocabHighlightService

vocab_highlight_routes = Blueprint('vocab_highlights', __name__, url_prefix='/vocab_highlights')

@vocab_highlight_routes.route('/process', methods=['POST'])
def process_highlights():
    try:
        # Directly invoke the processing of new vocab highlights
        VocabHighlightService.process_new_vocab_highlights()
        return jsonify({"success": True, "message": "Vocab highlights processed successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@vocab_highlight_routes.route('/request_permission', methods=['POST'])
def request_permission():
    try:
        # Request permission from AnkiConnect
        result = AnkiService.request_connection_permission()
        return jsonify({"success": True, "result": result}), 200 if result else 403
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Additional route to update a specific vocab highlight and its corresponding Anki card
@vocab_highlight_routes.route('/update/<int:highlight_id>', methods=['POST'])
def update_highlight(highlight_id):
    try:
        data = request.json
        updated_usage = data.get('usage', None)
        if updated_usage:
            VocabHighlightService.update_anki_card(highlight_id, updated_usage)
            return jsonify({"success": True, "message": "Vocab highlight and corresponding Anki card updated successfully."}), 200
        else:
            return jsonify({"success": False, "message": "Usage data is required."}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Feel free to add more routes as needed, such as for deleting vocab highlights or fetching specific details.
