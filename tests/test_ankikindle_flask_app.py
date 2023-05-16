import os
import shutil
import time

import pytest
import sqlite3
import tempfile
import threading
import ankiconnect_wrapper
import ankikindle_flask_app
from . import test_util
from .. import ankikindle
from .conftest import logger
from unittest.mock import patch
from .test_util import TEST_VOCAB_DB_FILE


@pytest.mark.skip("this test is only to test the speed in which the os mounts and unmounts the kindle")
def test_continuous_mount_unmount_logging(client):
    with patch('ankikindle_flask_app.on_mounted'):
        ankikindle_flask_app.watch_for_kindle_mount(client, "/Volumes", "Kindle")


def simulate_kindle_device_mounting(temp_dir: tempfile.TemporaryDirectory, ready_for_mount_event: threading.Event,
                                    db_temp_file_ready_for_processing_event: threading.Event()):
    ready_for_mount_event.wait()
    shutil.copy(TEST_VOCAB_DB_FILE, os.path.join(temp_dir.name, 'vocab.db'))
    db_temp_file_ready_for_processing_event.set()
    logger.info(f"Kindle directory created and test vocab.db copied to {temp_dir.name}/vocab.db (simulated mount)")


def simulate_kindle_device_mounting_with_db_update(temp_dir: tempfile.TemporaryDirectory,
                                                   ready_for_mount_event: threading.Event,
                                                   db_temp_file_ready_for_processing_event: threading.Event()):
    ready_for_mount_event.wait()
    shutil.copy(TEST_VOCAB_DB_FILE, os.path.join(temp_dir.name, 'vocab.db'))
    # TODO figure out good practice for optional method parameters and the add word lookups method
    db_update_ready_event = threading.Event()
    db_update_ready_event.set()
    db_update_processed_event = threading.Event()
    db_update_processed_event.set()
    test_util.add_word_lookups_to_db(temp_dir.name, db_update_ready_event, db_update_processed_event, threading.Event())
    db_temp_file_ready_for_processing_event.set()
    logger.info(f"Kindle directory created and test vocab.db copied to {temp_dir.name}/vocab.db (simulated mount)")


def monitor_kindle_mount_status_for_tests(ankiconnect_injection: ankiconnect_wrapper,
                                          ready_for_mount_event: threading.Event,
                                          db_temp_file_ready_for_processing_event: threading.Event,
                                          temp_dir: tempfile.TemporaryDirectory,
                                          log_messages: list,
                                          number_of_mounts_to_be_tested: int,
                                          is_a_real_mount: bool):
    mounted = False
    processed_mounts = 0
    while processed_mounts < number_of_mounts_to_be_tested:
        if db_temp_file_ready_for_processing_event.is_set() and os.path.exists(os.path.join(temp_dir.name, 'vocab.db')) and not mounted:
            mounted = True
            logger.info('Kindle mounted')
            log_messages.append('Kindle mounted')
            connection_injection = sqlite3.connect(os.path.join(temp_dir.name, 'vocab.db'))
            try:
                # TODO do not mock the ankiconnect_injection and instead do a full addition to anki and then remove the card
                ankikindle.process_new_vocab_highlights(connection_injection, ankiconnect_injection)
                processed_mounts += 1
                logger.info(f"processed mount event {processed_mounts}")
                log_messages.append(f"processed mount event {processed_mounts}")
            finally:
                connection_injection.close()
                test_util.remove_temp_db_file(temp_dir.name)
                db_temp_file_ready_for_processing_event.clear()  # unset the event after first process

        elif not os.path.exists(os.path.join(temp_dir.name, 'vocab.db')) and mounted:
            mounted = False
            logger.info('Kindle unmounted')
            log_messages.append('Kindle unmounted')
        ready_for_mount_event.set()
    logger.info("watch_for_kindle_mount_TEST_wrapper thread stopped")


#@pytest.mark.skip("t")
def test_basic_integration_with_kindle_mounting_and_db_processing():
    ready_for_mount_event = threading.Event()
    db_temp_file_ready_for_processing_event = threading.Event()

    temp_dir = tempfile.TemporaryDirectory()
    log_messages = []
    number_of_mounts_to_be_tested = 2
    is_a_real_mount = False
    watch_kindle_mounting_event_thread = threading.Thread(target=monitor_kindle_mount_status_for_tests,
                                                          args=(ankiconnect_wrapper,
                                                                ready_for_mount_event,
                                                                db_temp_file_ready_for_processing_event,
                                                                temp_dir,
                                                                log_messages,
                                                                number_of_mounts_to_be_tested,
                                                                is_a_real_mount))
    watch_kindle_mounting_event_thread.start()

    logger.info("Begin first simulated mount with unchanged test db")
    simulate_kindle_device_mounting(temp_dir, ready_for_mount_event, db_temp_file_ready_for_processing_event)
    time.sleep(3)  # no idea

    logger.info("Begin second simulated mount after updating test db")
    simulate_kindle_device_mounting_with_db_update(temp_dir, ready_for_mount_event, db_temp_file_ready_for_processing_event)
    assert log_messages == ['Kindle mounted', 'Processed mount event 1', 'Kindle unmounted',
                            'Kindle mounted', 'Processed mount event 2', 'Kindle unmounted']

    watch_kindle_mounting_event_thread.join()

    assert os.path.exists(os.path.join(temp_dir.name, 'vocab.db'))
    assert not watch_kindle_mounting_event_thread.is_alive()

    # TODO add more asserts about the state of the database after processing

    logger.info("full end to end basic integration test completed")
