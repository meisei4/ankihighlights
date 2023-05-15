import os
import logging
import ankiconnect_wrapper
from flask import Flask
from ankikindle_flask_routes import register_process_new_vocab_highlights_route

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s')
logger = logging.getLogger(__name__)


def on_mounted(flask_app: Flask):
    with flask_app.test_client() as client:
        headers = {'Content-type': 'application/json'}
        client.post("/process_new_vocab_highlights", json={}, headers=headers)


def watch_for_kindle_mount(flask_app: Flask, mount_dir_root: str, kindle_device_name: str):
    mounted = False
    while True:
        dirs = [d for d in os.listdir(mount_dir_root) if os.path.isdir(os.path.join(mount_dir_root, d))]
        if kindle_device_name in dirs and not mounted:
            # TODO figure out how to allow for an OS independent mount location
            #   例えば MacOS default mount location: "/Volumes/Kindle/system/vocabulary/vocab.db"
            vocab_db_path = os.path.join(mount_dir_root, kindle_device_name, 'system', 'vocabulary', 'vocab.db')
            if os.path.exists(vocab_db_path):
                on_mounted(flask_app)
                mounted = True
                logger.info(f'{kindle_device_name} mounted')
        elif kindle_device_name not in dirs and mounted:
            mounted = False
            logger.info(f"{kindle_device_name} unmounted")


def register_flask_routes(flask_app: Flask, ankikindle_injection,
                          ankiconnect_injection: ankiconnect_wrapper,
                          kindle_mount_location):
    register_process_new_vocab_highlights_route(flask_app,
                                                ankikindle_injection,
                                                ankiconnect_injection,
                                                kindle_mount_location)


# TODO i have no idea how Flask works, but i assume it will be useful if i go ahead with containerization of this app
'''
if __name__ == '__main__':
    app = Flask(__name__)
    register_flask_routes(app, ankikindle, ankiconnect_wrapper)
    thread = threading.Thread(target=watch_for_kindle_mount)
    thread.start()
    app.run(host='0.0.0.0', port=5000)
'''
