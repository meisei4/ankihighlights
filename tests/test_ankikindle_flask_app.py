import os
import pytest
import sqlite3
import logging
import threading
import ankikindle
import ankiconnect_wrapper
import ankikindle_flask_app
import vocab_db_accessor_wrap
from flask import Flask
from unittest.mock import patch


logging.basicConfig(filename='test_app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@pytest.mark.skip("this test is only to test the speed in which the os mounts and unmounts the kindle")
def test_infinite_mount_and_unmount_logging_INTEGRATION(client):
    with patch('ankikindle_flask_app.on_mounted'):
        ankikindle_flask_app.watch_for_kindle_mount(client)


def test_integration_with_flask():
    flask_app = Flask(__name__)
    ankikindle_flask_app.register_flask_routes(flask_app, ankikindle, ankiconnect_wrapper)
    watch_kindle_mounting_event_thread = threading.Thread(target=ankikindle_flask_app.watch_for_kindle_mount,
                                                          args=(flask_app, ))
    watch_kindle_mounting_event_thread.start()
    flask_app.run()


def watch_for_kindle_mount_TEST_wrapper(ankikindle_injection: ankikindle, ankiconnect_wrapper_injection: ankiconnect_wrapper):
    mounted = False
    while True:
        dirs = [d for d in os.listdir("/Volumes") if os.path.isdir(os.path.join("/Volumes", d))]
        if "Kindle" in dirs and not mounted:
            if os.path.exists(vocab_db_accessor_wrap.MACOS_TARGET_VOCAB_MOUNT_FILE_LOC):
                mounted = True
                logger.info('Kindle mounted')
                connection_injection = sqlite3.Connection(vocab_db_accessor_wrap.MACOS_TARGET_VOCAB_MOUNT_FILE_LOC)
                ankikindle_injection.process_new_vocab_highlights(connection_injection, ankiconnect_wrapper_injection)

                #  TODO APPARENTLY THIS FUCKING process FUNCTION DOESNT EXIST (imprto of some shit)"!!!!! __I DONT BELIEVE IT!!!!
        elif "Kindle" not in dirs and mounted:
            mounted = False
            logger.info('Kindle unmounted')


def test_integration_vanilla():
    watch_kindle_mounting_event_thread = threading.Thread(target=watch_for_kindle_mount_TEST_wrapper)
    watch_kindle_mounting_event_thread.start()
