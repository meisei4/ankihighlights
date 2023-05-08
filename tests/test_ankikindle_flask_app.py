import pytest
import logging
import threading
from flask import Flask

import ankiconnect_wrapper
import ankikindle
import ankikindle_flask_app
from unittest.mock import patch, Mock

logging.basicConfig(filename='test_app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


@pytest.mark.skip("this test is only to test the speed in which the os mounts and unmounts the kindle")
def test_infinite_mount_and_unmount_logging_INTEGRATION(client):
    with patch('ankikindle_flask_app.on_mounted'):
        ankikindle_flask_app.watch_for_kindle_mount(client)


def test_integration():
    flask_app = Flask(__name__)
    ankikindle_flask_app.register_flask_routes(flask_app, ankikindle, ankiconnect_wrapper)
    watch_kindle_mounting_event_thread = threading.Thread(target=ankikindle_flask_app.watch_for_kindle_mount,
                                                          args=(flask_app, ))
    watch_kindle_mounting_event_thread.start()
    flask_app.run()
