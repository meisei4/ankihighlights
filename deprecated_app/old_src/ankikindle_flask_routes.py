import sqlite3
import ankiconnect_wrapper
from flask import jsonify, Flask


def register_process_new_vocab_highlights_route(flask_app: Flask, ankikindle_injection,
                                                ankiconnect_injection: ankiconnect_wrapper,
                                                kindle_mount_location: str):
    @flask_app.route('/process_new_vocab_highlights', methods=['POST'])
    def process_new_vocab_highlights_route():
        connection_injection = sqlite3.Connection(kindle_mount_location)
        vocab_highlights = ankikindle_injection.process_new_vocab_highlights(connection_injection, ankiconnect_injection)
        if vocab_highlights:
            return jsonify({"message": "New vocab highlights processed", "highlights": vocab_highlights})
        return jsonify({"message": "No new vocab highlights to process"})

    return process_new_vocab_highlights_route
