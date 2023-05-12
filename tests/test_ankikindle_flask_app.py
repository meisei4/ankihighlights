import os
import shutil
import pytest
import sqlite3
import tempfile
import threading
import ankiconnect_wrapper
import ankikindle_flask_app
from .. import ankikindle
from .conftest import logger
from unittest.mock import patch
from .test_util import TEST_VOCAB_DB_FILE


@pytest.mark.skip("this test is only to test the speed in which the os mounts and unmounts the kindle")
def test_continuous_mount_unmount_logging(client):
    with patch('ankikindle_flask_app.on_mounted'):
        ankikindle_flask_app.watch_for_kindle_mount(client, "/Volumes", "Kindle")


def simulate_kindle_device_mounting(temp_dir: tempfile.TemporaryDirectory, ready_for_mount_event: threading.Event,
                                    db_temp_file_copy_finished_event: threading.Event()):
    ready_for_mount_event.wait()
    shutil.copy(TEST_VOCAB_DB_FILE, os.path.join(temp_dir.name, 'vocab.db'))
    db_temp_file_copy_finished_event.set()
    logger.info(f"Kindle directory created and test vocab.db copied to {temp_dir.name}/vocab.db (simulated mount)")


def monitor_kindle_mount_status_for_tests(ankiconnect_injection: ankiconnect_wrapper,
                                          ready_for_mount_event: threading.Event,
                                          db_temp_file_copy_finished_event: threading.Event,
                                          processed_new_vocab_highlights_event: threading.Event,
                                          temp_dir: tempfile.TemporaryDirectory):
    mounted = False
    while not processed_new_vocab_highlights_event.is_set():
        if db_temp_file_copy_finished_event.is_set() and os.path.exists(temp_dir.name) and not mounted:
            mounted = True
            logger.info('Kindle mounted')
            connection_injection = sqlite3.connect(os.path.join(temp_dir.name, 'vocab.db'))
            with connection_injection:
                ankikindle.process_new_vocab_highlights(connection_injection, ankiconnect_injection)
                processed_new_vocab_highlights_event.set()

        elif not os.path.exists(temp_dir.name) and mounted:
            mounted = False
            logger.info('Kindle unmounted')
        ready_for_mount_event.set()
    logger.info("watch_for_kindle_mount_TEST_wrapper thread stopped")


def test_basic_integration_with_kindle_mounting_and_db_processing():
    ready_for_mount_event = threading.Event()
    db_temp_file_copy_finished_event = threading.Event()
    processed_new_vocab_highlights_event = threading.Event()

    temp_dir = tempfile.TemporaryDirectory()

    watch_kindle_mounting_event_thread = threading.Thread(target=monitor_kindle_mount_status_for_tests,
                                                          args=(ankiconnect_wrapper,
                                                                ready_for_mount_event,
                                                                db_temp_file_copy_finished_event,
                                                                processed_new_vocab_highlights_event,
                                                                temp_dir))
    watch_kindle_mounting_event_thread.start()

    simulate_kindle_device_mounting(temp_dir, ready_for_mount_event, db_temp_file_copy_finished_event)

    processed_new_vocab_highlights_event.wait()
    watch_kindle_mounting_event_thread.join()

    assert os.path.exists(os.path.join(temp_dir.name, 'vocab.db'))
    assert not watch_kindle_mounting_event_thread.is_alive()

    # TODO add more asserts about the state of the database after processing

    logger.info("test_integration_vanilla completed")
