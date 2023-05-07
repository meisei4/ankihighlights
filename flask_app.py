import threading
from flask import Flask
from sqlite3 import Connection
from routes import register_routes


def create_app(connection_injection, ankikindle_injection, ankiconnect_wrapper_injection):
    app = Flask(__name__)

    stop_event = threading.Event()
    thread = None
    register_routes(app, ankikindle_injection, ankiconnect_wrapper_injection, connection_injection, stop_event, thread)
    return app


if __name__ == '__main__':
    import ankikindle as main_ankikindle_injection
    import ankiconnect_wrapper as main_ankiconnect_wrapper_injection

    main_connection_injection = Connection("")  # Replace with your actual database file path

    main_app = create_app(main_connection_injection, main_ankikindle_injection, main_ankiconnect_wrapper_injection)

    main_app.run(host='0.0.0.0', port=5000)
