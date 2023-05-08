import sqlite3

import ankiconnect_wrapper
import ankikindle
import vocab_db_accessor_wrap
from flask import jsonify, Flask


def register_process_new_vocab_highlights_route(flask_app: Flask, ankikindle_injection: ankikindle,
                                                ankiconnect_injection: ankiconnect_wrapper):
    @flask_app.route('/process_new_vocab_highlights', methods=['POST'])
    def process_new_vocab_highlights_route():
        connection_injection = sqlite3.Connection(vocab_db_accessor_wrap.MACOS_TARGET_VOCAB_MOUNT_FILE_LOC)
        vocab_highlights = ankikindle_injection.process_new_vocab_highlights(connection_injection, ankiconnect_injection)
        if vocab_highlights:
            return jsonify({"message": "New vocab highlights processed", "highlights": vocab_highlights})
        return jsonify({"message": "No new vocab highlights to process"})

    return process_new_vocab_highlights_route
