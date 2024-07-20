from flask import Blueprint, jsonify, request

from app.models import LatestTimestamp
from app.services.highlight_service import HighlightService
from app.models.dto.lookup_dto import LookupDTO
from app.models.dto.latest_timestamp_dto import LatestTimestampDTO

highlight_routes = Blueprint('highlight', __name__, url_prefix='/highlight')

def handle_service_response(success, data=None, message=None, status_code=200):
    if success:
        return jsonify({"success": True, "data": data, "message": message}), status_code
    else:
        return jsonify({"success": False, "message": message or "An error occurred"}), status_code

@highlight_routes.route('/process', methods=['POST'])
def process_highlights():
    try:
        highlights = HighlightService.process_new_vocab_highlights()
        highlights_dto = [LookupDTO.to_dict(highlight) for highlight in highlights]
        return handle_service_response(True, data={"highlight": highlights_dto},
                                       message="highlights processed successfully.")
    except Exception as e:
        return handle_service_response(False, message=str(e), status_code=500)

@highlight_routes.route('/latest_timestamp', methods=['GET'])
def get_latest_timestamp():
    try:
        timestamp = HighlightService.get_latest_timestamp()
        timestamp_dto = LatestTimestampDTO.to_dict(LatestTimestamp(timestamp=timestamp))
        return handle_service_response(True, data={"timestamp": timestamp_dto},
                                       message="Latest timestamp retrieved successfully.")
    except Exception as e:
        return handle_service_response(False, message=str(e), status_code=500)

@highlight_routes.route('/word_lookups_after/<int:timestamp>', methods=['GET'])
def get_word_lookups_after(timestamp):
    try:
        lookups = HighlightService.get_word_lookups_after_timestamp(timestamp)
        lookups_dto = [LookupDTO.to_dict(lookup) for lookup in lookups]
        return handle_service_response(True, data={"lookups": lookups_dto}, message="Word lookups retrieved successfully.")
    except Exception as e:
        return handle_service_response(False, message=str(e), status_code=500)
