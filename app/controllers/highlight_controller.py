from flask import Blueprint, jsonify
from flask_injector import inject

from app.injection_dependencies import Dependencies
from app.models import LatestTimestamp

highlight_routes = Blueprint('highlight', __name__, url_prefix='/highlight')


def handle_service_response(success, data=None, message=None, status_code=200):
    if success:
        return jsonify({"success": True, "data": data, "message": message}), status_code
    else:
        return jsonify({"success": False, "message": message or "An error occurred"}), status_code


@highlight_routes.route('/process', methods=['POST'])
@inject
def process_highlights(deps: Dependencies):
    try:
        highlights = deps.highlight_service.process_new_vocab_highlights()
        highlights_dto = [deps.lookup_dto.to_dict(highlight) for highlight in highlights]
        return handle_service_response(True, data={"highlight": highlights_dto},
                                       message="highlights processed successfully.")
    except Exception as e:
        return handle_service_response(False, message=str(e), status_code=500)


@highlight_routes.route('/latest_timestamp', methods=['GET'])
@inject
def get_latest_timestamp(deps: Dependencies):
    try:
        timestamp = deps.highlight_service.get_latest_timestamp()
        timestamp_dto = deps.latest_timestamp_dto.to_dict(LatestTimestamp(timestamp=timestamp))
        return handle_service_response(True, data={"timestamp": timestamp_dto},
                                       message="Latest timestamp retrieved successfully.")
    except Exception as e:
        return handle_service_response(False, message=str(e), status_code=500)


@highlight_routes.route('/word_lookups_after/<int:timestamp>', methods=['GET'])
@inject
def get_word_lookups_after(deps: Dependencies, timestamp):
    try:
        lookups = deps.highlight_service.get_word_lookups_after_timestamp(timestamp)
        lookups_dto = [deps.lookup_dto.to_dict(lookup) for lookup in lookups]
        return handle_service_response(True, data={"lookups": lookups_dto},
                                       message="Word lookups retrieved successfully.")
    except Exception as e:
        return handle_service_response(False, message=str(e), status_code=500)


# Add a simple test endpoint
@highlight_routes.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({"success": True, "message": "Test endpoint is working!"}), 200
