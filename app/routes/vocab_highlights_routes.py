from flask import Blueprint
from flask import jsonify, request

from app.services.anki_service import AnkiService
from app.services.vocab_highlight_service import VocabHighlightService

vocab_highlight_routes = Blueprint('vocab_highlights', __name__, url_prefix='/vocab_highlights')


def handle_service_response(success, data=None, message=None, status_code=200):
    if success:
        return jsonify({"success": True, "data": data, "message": message}), status_code
    else:
        return jsonify({"success": False, "message": message or "An error occurred"}), status_code


@vocab_highlight_routes.route('/process', methods=['POST'])
def process_highlights():
    try:
        VocabHighlightService.process_new_vocab_highlights()
        return handle_service_response(True, message="Vocab highlights processed successfully.")
    except Exception as e:
        return handle_service_response(False, message=str(e), status_code=500)


@vocab_highlight_routes.route('/request_permission', methods=['POST'])
def request_permission():
    response = AnkiService.request_connection_permission()
    if 'error' not in response:
        return handle_service_response(True, data={"permission_granted": response},
                                       message="Permission request processed.")
    else:
        return handle_service_response(False, message=response['error'], status_code=403)


@vocab_highlight_routes.route('/update/<int:highlight_id>', methods=['POST'])
def update_highlight(highlight_id):
    data = request.json
    updated_usage = data.get('usage', None)
    if not updated_usage:
        return handle_service_response(False, message="Usage data is required.", status_code=400)

    try:
        updated = VocabHighlightService.update_anki_card(highlight_id, updated_usage)
        if updated:
            return handle_service_response(True,
                                           message="Vocab highlight and corresponding Anki card updated successfully.")
        else:
            return handle_service_response(False, message="Highlight ID not found or update failed.", status_code=404)
    except Exception as e:
        return handle_service_response(False, message=str(e), status_code=500)
