import threading
from flask import jsonify, request


def register_routes(app, ankikindle_module, ankiconnect_module, connection, stop_event, main_thread):
    register_start_route(app, ankikindle_module, connection, ankiconnect_module, stop_event, main_thread)
    register_stop_route(app, ankikindle_module, stop_event, main_thread)
    register_note_route(app, ankikindle_module, ankiconnect_module)
    register_process_new_vocab_highlights_route(app, ankikindle_module, connection, ankiconnect_module)


def register_start_route(app, ankikindle_module, connection_injection, ankiconnect_injection, stop_event, main_thread):
    def start_main_thread():
        nonlocal main_thread
        if main_thread is None or not main_thread.is_alive():
            main_thread = threading.Thread(target=ankikindle_module.main,
                                           args=(connection_injection, ankiconnect_injection, stop_event))
            main_thread.start()

    @app.route('/start', methods=['POST'])
    def start_process():
        if not ankikindle_module.is_running():
            start_main_thread()
            return jsonify({"message": "Process started"})
        else:
            return jsonify({"message": "Process already running"})

    return start_process


def register_stop_route(app, ankikindle_module, stop_event, main_thread):
    def stop_main_thread():
        nonlocal main_thread
        if main_thread is not None:
            ankikindle_module.stop_ankikindle(stop_event, main_thread)
            main_thread = None

    @app.route('/stop', methods=['POST'])
    def stop_process():
        if not ankikindle_module.is_running():
            return jsonify({"message": "Process not running"})

        stop_main_thread()

        return jsonify({"message": "Process stopped"})

    return stop_process


def register_note_route(app, ankikindle_module, ankiconnect_injection):
    @app.route('/add_or_update_note', methods=['POST'])
    def add_or_update():
        data = request.json
        word_highlight = data['word_highlight']
        deck_name = data['deck_name']
        card_type = data['card_type']

        note_id = ankikindle_module.add_or_update_note(word_highlight, deck_name, card_type, ankiconnect_injection)
        return jsonify({"note_id": note_id})

    return add_or_update


def register_process_new_vocab_highlights_route(app, ankikindle_module, connection_injection, ankiconnect_injection):
    @app.route('/process_new_vocab_highlights', methods=['POST'])
    def process_new_vocab_highlights_route():
        latest_timestamp = ankikindle_module.process_new_vocab_highlights(connection_injection, ankiconnect_injection)

        return jsonify({"message": "New vocab highlights processed", "latest_timestamp": latest_timestamp})

    return process_new_vocab_highlights_route
