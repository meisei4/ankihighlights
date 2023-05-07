import os
import threading
import requests
from flask import Flask

import vocab_db_accessor_wrap
from ankikindle_flask_routes import register_process_new_vocab_highlights_route


def create_app(ankikindle_injection, ankiconnect_wrapper_injection):
    app = Flask(__name__)
    register_process_new_vocab_highlights_route(app, ankikindle_injection, ankiconnect_wrapper_injection)
    return app


def on_mounted():
    url = "http://localhost:5000/process_new_vocab_highlights"
    headers = {'Content-type': 'application/json'}
    r = requests.post(url, json={}, headers=headers)
    r.raise_for_status()


def watch_for_kindle_mount():
    mounted = False
    while True:
        dirs = [d for d in os.listdir("/Volumes") if os.path.isdir(os.path.join("/Volumes", d))]
        if "Kindle" in dirs and not mounted:
            if os.path.exists(vocab_db_accessor_wrap.MACOS_TARGET_VOCAB_MOUNT_FILE_LOC):
                on_mounted()
                mounted = True
        elif "Kindle" not in dirs and mounted:
            mounted = False


if __name__ == '__main__':
    import ankikindle as main_ankikindle_injection
    import ankiconnect_wrapper as main_ankiconnect_wrapper_injection

    main_app = create_app(main_ankikindle_injection, main_ankiconnect_wrapper_injection)

    thread = threading.Thread(target=watch_for_kindle_mount)
    thread.start()

    main_app.run(host='0.0.0.0', port=5000)
