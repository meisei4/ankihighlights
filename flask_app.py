import threading
import ankikindle as ankikindle_injection
import ankiconnect_wrapper as ankiconnect_wrapper_injection
from flask import Flask
from sqlite3 import Connection
from routes import register_start_route, register_stop_route, register_note_route, register_process_new_vocab_highlights_route

app = Flask(__name__)

stop_event = threading.Event()
thread = None
connection_injection = Connection("your_database_file.db")  # Replace with your actual database file path

register_start_route(app, ankikindle_injection, connection_injection, ankiconnect_wrapper_injection, stop_event, thread)
register_stop_route(app, ankikindle_injection, stop_event, thread)
register_note_route(app, ankikindle_injection, ankiconnect_wrapper_injection)
register_process_new_vocab_highlights_route(app, ankikindle_injection, connection_injection, ankikindle_injection, )


def check_and_create_latest_timestamp_table(connection: Connection):
    cursor = connection.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS latest_timestamp (
                id INTEGER PRIMARY KEY,
                timestamp INTEGER
            )
    """)
    connection.commit()


if __name__ == '__main__':
    check_and_create_latest_timestamp_table(connection_injection)
    app.run(host='0.0.0.0', port=5000)


