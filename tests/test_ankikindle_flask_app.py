import os
import shutil
import time
from sqlite3 import Connection

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
        ankikindle_flask_app.watch_for_kindle_mount_flask(client, "/Volumes", "Kindle")

pytest.mark.skip("this is not working because the lookup_timestamp isnt being created, figure out how to get that created")
def test_basic_integration_with_kindle_mounting_and_db_processing(db_connection: Connection, temp_db_directory: str):
    ready_for_first_mount_event = threading.Event()
    ready_for_following_mount_events = threading.Event()
    db_temp_file_ready_for_processing_event = threading.Event()
    all_kindle_mounts_finished_event = threading.Event()

    temp_dir = tempfile.TemporaryDirectory()
    temp_db_file_path = test_util.get_test_temp_db_file_name(temp_dir.name)
    log_messages = []
    number_of_mounts_to_be_tested = 2
    is_a_real_mount = False
    watch_kindle_mounting_event_thread = threading.Thread(target=monitor_kindle_mount_status_for_tests,
                                                          args=(ankiconnect_wrapper,
                                                                ready_for_first_mount_event,
                                                                ready_for_following_mount_events,
                                                                db_temp_file_ready_for_processing_event,
                                                                all_kindle_mounts_finished_event,
                                                                temp_db_file_path,
                                                                log_messages,
                                                                number_of_mounts_to_be_tested,
                                                                is_a_real_mount))
    logger.info("Starting watch_kindle_mounting_event_thread")
    watch_kindle_mounting_event_thread.start()
    ready_for_first_mount_event.set()
    logger.info("ready_for_first_mount_event set")

    logger.info("Begin first simulated mount with unchanged test db")

    simulate_kindle_device_mounting(temp_db_file_path, db_temp_file_ready_for_processing_event)

    ready_for_following_mount_events.wait()
    logger.info("Received ready_for_following_mount_events")

    logger.info("Begin second simulated mount after updating test db")
    simulate_kindle_device_mounting_with_db_update(temp_db_file_path, db_temp_file_ready_for_processing_event)

    all_kindle_mounts_finished_event.wait()
    logger.info("Received all_kindle_mounts_finished_event")

    watch_kindle_mounting_event_thread.join()
    # TODO technically the Kindle unmounted should show up the second time around but the loop skips it
    assert log_messages == ['Kindle mounted', 'processed mount event 1', 'Kindle unmounted',
                            'Kindle mounted', 'processed mount event 2']

    logger.info("monitor_kindle_mount_status_for_tests thread stopped")

    assert not os.path.exists(temp_db_file_path)
    assert not watch_kindle_mounting_event_thread.is_alive()

    # TODO add more asserts about the state of the database after processing

    logger.info("full end to end basic integration test completed")


def monitor_kindle_mount_status_for_tests(ankiconnect_injection: ankiconnect_wrapper,
                                          ready_for_first_mount_event: threading.Event,
                                          ready_for_following_mount_events: threading.Event,
                                          db_temp_file_ready_for_processing_event: threading.Event,
                                          all_kindle_mounts_finished_event: threading.Event,
                                          temp_db_file_path: str,
                                          log_messages: list,
                                          number_of_mounts_to_be_tested: int,
                                          is_a_real_mount: bool):
    ready_for_first_mount_event.wait()
    logger.info("Received ready_for_first_mount_event")
    mounted = False
    processed_mounts = 0
    while processed_mounts < number_of_mounts_to_be_tested:
        logger.info("monitor_kindle_mount_status_for_tests loop started")
        if db_temp_file_ready_for_processing_event.is_set() and os.path.exists(temp_db_file_path) and not mounted:
            mounted = True
            logger.info('Kindle mounted')
            log_messages.append('Kindle mounted')
            connect_to_db_and_process_potential_new_vocab_lookups_then_disconnect_and_delete_db(ankiconnect_injection,
                                                                                                temp_db_file_path,
                                                                                                db_temp_file_ready_for_processing_event)
            processed_mounts += 1
            logger.info(f"Processed mount event {processed_mounts}")
            log_messages.append(f"Processed mount event {processed_mounts}")
            db_temp_file_ready_for_processing_event.clear()
            logger.info("db_temp_file_ready_for_processing_event cleared")
            ready_for_following_mount_events.set()
            logger.info("ready_for_following_mount_events set")

        elif not os.path.exists(temp_db_file_path) and mounted:
            mounted = False
            logger.info('Kindle unmounted')
            log_messages.append('Kindle unmounted')

        time.sleep(2)

    all_kindle_mounts_finished_event.set()
    logger.info("all_kindle_mounts_finished_event set")
    logger.info("Exiting monitor_kindle_mount_status_for_tests loop")


def simulate_kindle_device_mounting(temp_db_file_path: str,
                                    db_temp_file_ready_for_processing_event: threading.Event):
    shutil.copy(TEST_VOCAB_DB_FILE, temp_db_file_path)
    db_temp_file_ready_for_processing_event.set()
    logger.info(f"Kindle directory created and test vocab.db copied to {temp_db_file_path} (simulated mount)")
    logger.info("db_temp_file_ready_for_processing_event set in simulate_kindle_device_mounting")


def simulate_kindle_device_mounting_with_db_update(temp_db_file_path: str,
                                                   db_temp_file_ready_for_processing_event: threading.Event):
    shutil.copy(TEST_VOCAB_DB_FILE, temp_db_file_path)
    db_update_ready_event = threading.Event()
    db_update_ready_event.set()
    db_update_processed_event = threading.Event()
    db_update_processed_event.set()
    test_util.add_word_lookups_to_db_for_non_main_thread(temp_db_file_path, db_update_ready_event,
                                                         db_update_processed_event,
                                                         threading.Event())
    db_temp_file_ready_for_processing_event.set()
    logger.info(
        f"Kindle directory created and test vocab.db copied to {temp_db_file_path} (simulated mount and db update)")
    logger.info("db_temp_file_ready_for_processing_event set in simulate_kindle_device_mounting_with_db_update")


def connect_to_db_and_process_potential_new_vocab_lookups_then_disconnect_and_delete_db(
        ankiconnect_injection: ankiconnect_wrapper,
        temp_db_file_path: str,
        db_temp_file_ready_for_processing_event: threading.Event):
    connection_injection = sqlite3.connect(temp_db_file_path)
    try:
        ankikindle.process_new_vocab_highlights(connection_injection, ankiconnect_injection)
    finally:
        connection_injection.close()
        test_util.remove_temp_db_file(temp_db_file_path)
        logger.info("Database connection closed and temporary database file removed")
        db_temp_file_ready_for_processing_event.clear()
        logger.info("db_temp_file_ready_for_processing_event cleared in connect_to_db_and_process_potential_new_vocab_lookups_then_disconnect_and_delete_db")
