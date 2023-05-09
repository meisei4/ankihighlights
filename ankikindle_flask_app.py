import os
import logging
import ankiconnect_wrapper
import vocab_db_accessor_wrap
from flask import Flask
from ankikindle_flask_routes import register_process_new_vocab_highlights_route

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


# TODO this is probably doing nothing
def on_mounted(flask_app: Flask):
    with flask_app.test_client() as client:
        headers = {'Content-type': 'application/json'}
        client.post("/process_new_vocab_highlights", json={}, headers=headers)


def watch_for_kindle_mount(flask_app: Flask):
    mounted = False
    while True:
        dirs = [d for d in os.listdir("/Volumes") if os.path.isdir(os.path.join("/Volumes", d))]
        if "Kindle" in dirs and not mounted:
            if os.path.exists(vocab_db_accessor_wrap.MACOS_TARGET_VOCAB_MOUNT_FILE_LOC):
                on_mounted(flask_app)
                mounted = True
                logger.info('Kindle mounted')
        elif "Kindle" not in dirs and mounted:
            mounted = False
            logger.info('Kindle unmounted')


def register_flask_routes(flask_app: Flask, ankikindle_injection,
                          ankiconnect_wrapper_injection: ankiconnect_wrapper):
    register_process_new_vocab_highlights_route(flask_app, ankikindle_injection, ankiconnect_wrapper_injection)

'''
if __name__ == '__main__':
    app = Flask(__name__)
    register_flask_routes(app, ankikindle, ankiconnect_wrapper)
    thread = threading.Thread(target=watch_for_kindle_mount)
    thread.start()
    app.run(host='0.0.0.0', port=5000)
'''