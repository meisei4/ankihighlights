import os
import time
import pytest
import logging
import requests
import threading
import ankikindle
import ankiconnect_wrapper
from unittest.mock import Mock
from ankikindle_flask_app import create_app, watch_for_kindle_mount


def test_create_app():
    ankikindle_injection = Mock()
    ankiconnect_wrapper_injection = Mock()

    app = create_app(ankikindle_injection, ankiconnect_wrapper_injection)

    assert app is not None
    # Add more assertions to check if the app has the correct configuration or routes, if necessary


@pytest.mark.skip(reason="test is for kindle mounting only")
def test_integration():
    LOG_FILENAME = 'test_app.log'

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(LOG_FILENAME)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    main_app = create_app(ankikindle, ankiconnect_wrapper)
    watch_thread = threading.Thread(target=watch_for_kindle_mount, args=(logger,))
    watch_thread.start()

    main_app.run()

    response = requests.get("http://localhost:5000/")
    assert response.status_code == 200

    input("Please mount your Kindle. Press Enter when ready.")

    response = requests.post("http://localhost:5000/process_new_vocab_highlights", json={})
    assert response.status_code == 200
    assert "No new vocab highlights to process" in response.json()["message"]

    input("Please unmount your Kindle. Press Enter when done.")
    time.sleep(5)

    input("Please read a book and look up a vocab word then mount the kindle again. Press Enter when ready.")

    response = requests.post("http://localhost:5000/process_new_vocab_highlights", json={})
    assert response.status_code == 200
    assert "New vocab highlights" in response.json()["message"]

    watch_thread.join()
    os.remove(LOG_FILENAME)
