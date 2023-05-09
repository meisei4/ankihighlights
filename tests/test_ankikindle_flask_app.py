import os
import shutil
import time
import typing
from sqlite3 import Connection

import pytest
import sqlite3
import logging
import threading
import ankiconnect_wrapper
import ankikindle_flask_app
import vocab_db_accessor_wrap
from .. import ankikindle
from unittest.mock import patch
from tests.test_vocab_db_wrapper import TEST_VOCAB_DB_FILE

logging.basicConfig(filename='test_app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

KINDLE_DIRECTORY = "/Volumes/Kindle"
VOCAB_DB_TARGET_DIRECTORY = "/Volumes/Kindle/system/vocabulary"


@pytest.mark.skip("this test is only to test the speed in which the os mounts and unmounts the kindle")
def test_infinite_mount_and_unmount_logging_INTEGRATION(client):
    with patch('ankikindle_flask_app.on_mounted'):
        ankikindle_flask_app.watch_for_kindle_mount(client)


# Other imports and functions remain the same

def simulate_kindle_mounting(ready_for_mount_event: threading.Event):
    ready_for_mount_event.wait()
    if not os.path.exists(KINDLE_DIRECTORY):
        os.makedirs(VOCAB_DB_TARGET_DIRECTORY)
        shutil.copy(TEST_VOCAB_DB_FILE, os.path.join(VOCAB_DB_TARGET_DIRECTORY, 'vocab.db'))
        logger.info("Kindle directory created and vocab.db copied (simulated mount)")


def simulate_kindle_unmount(stop_event: threading.Event):
    if os.path.exists(KINDLE_DIRECTORY):
        shutil.rmtree(KINDLE_DIRECTORY)
        logger.info("Kindle directory removed (simulated unmount)")

    stop_event.set()


def watch_for_kindle_mount_TEST_wrapper(ankiconnect_injection: ankiconnect_wrapper,
                                        ready_for_mount_event: threading.Event,
                                        processed_new_vocab_highlights_event: threading.Event,
                                        stop_event: threading.Event):
    mounted = False
    while not stop_event.is_set() and not processed_new_vocab_highlights_event.is_set():
        dirs = [d for d in os.listdir("/Volumes") if os.path.isdir(os.path.join("/Volumes", d))]
        if "Kindle" in dirs and not mounted:
            if os.path.exists(vocab_db_accessor_wrap.MACOS_TARGET_VOCAB_MOUNT_FILE_LOC):
                mounted = True
                logger.info('Kindle mounted')
                connection_injection = sqlite3.Connection(vocab_db_accessor_wrap.MACOS_TARGET_VOCAB_MOUNT_FILE_LOC)
                with connection_injection:
                    ankikindle.process_new_vocab_highlights(connection_injection, ankiconnect_injection)
                    processed_new_vocab_highlights_event.set()

        elif "Kindle" not in dirs and mounted:
            mounted = False
            logger.info('Kindle unmounted')
        ready_for_mount_event.set()
    logger.info("watch_for_kindle_mount_TEST_wrapper thread stopped")


def test_integration_vanilla():
    stop_event = threading.Event()
    processed_new_vocab_highlights_event = threading.Event()
    ready_for_mount_event = threading.Event()

    watch_kindle_mounting_event_thread = threading.Thread(target=watch_for_kindle_mount_TEST_wrapper,
                                                          args=(ankiconnect_wrapper,
                                                                ready_for_mount_event,
                                                                processed_new_vocab_highlights_event,
                                                                stop_event))
    watch_kindle_mounting_event_thread.start()

    simulate_kindle_mounting(ready_for_mount_event)

    processed_new_vocab_highlights_event.wait()

    watch_kindle_mounting_event_thread.join()
    #TODO figure out how to get the connection closed properly (some how the with is not closing the connection to the db??
    #simulate_kindle_unmount(stop_event)
    logger.info("test_integration_vanilla completed")
