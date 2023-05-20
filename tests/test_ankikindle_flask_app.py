import os
import shutil
import pytest
import sqlite3
import tempfile
import threading
import ankiconnect_wrapper
from . import test_util
from .. import ankikindle
from .conftest import logger
from .test_util import TEST_VOCAB_DB_FILE


# @pytest.mark.skip("resigning for today at work, this isn't working after refactoring for the unit tests to work")
def test_basic_integration_with_kindle_mounting_and_db_processing():
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
    watch_kindle_mounting_event_thread.start()

    logger.info("Begin first simulated mount with unchanged test db")
    ready_for_first_mount_event.wait()
    simulate_kindle_device_mounting(temp_db_file_path, db_temp_file_ready_for_processing_event)

    ready_for_following_mount_events.wait()

    logger.info("Begin second simulated mount after updating test db")
    simulate_kindle_device_mounting_with_db_update(temp_db_file_path, db_temp_file_ready_for_processing_event)

    all_kindle_mounts_finished_event.wait()
    watch_kindle_mounting_event_thread.join()
    logger.info("monitor_kindle_mount_status_for_tests thread stopped")

    # TODO technically the Kindle unmounted should show up the second time around but the loop skips it
    assert log_messages == ['Kindle mounted', 'processed mount event 1', 'Kindle unmounted',
                            'Kindle mounted', 'processed mount event 2']

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
    mounted = False
    processed_mounts = 0
    while processed_mounts < number_of_mounts_to_be_tested:
        if db_temp_file_ready_for_processing_event.is_set() and os.path.exists(temp_db_file_path) and not mounted:
            mounted = True
            logger.info('Kindle mounted')
            log_messages.append('Kindle mounted')
            connect_to_db_and_process_potential_new_vocab_lookups_then_disconnect_and_delete_db(ankiconnect_injection,
                                                                                                temp_db_file_path,
                                                                                                db_temp_file_ready_for_processing_event)
            processed_mounts += 1
            logger.info(f"processed mount event {processed_mounts}")
            log_messages.append(f"processed mount event {processed_mounts}")

        elif not os.path.exists(temp_db_file_path) and mounted:
            mounted = False
            logger.info('Kindle unmounted')
            log_messages.append('Kindle unmounted')
            ready_for_following_mount_events.set()
        ready_for_first_mount_event.set()
    all_kindle_mounts_finished_event.set()


def simulate_kindle_device_mounting(temp_db_file_path: str,
                                    db_temp_file_ready_for_processing_event: threading.Event):
    shutil.copy(TEST_VOCAB_DB_FILE, temp_db_file_path)
    db_temp_file_ready_for_processing_event.set()
    logger.info(f"Kindle directory created and test vocab.db copied to {temp_db_file_path} (simulated mount)")


def simulate_kindle_device_mounting_with_db_update(temp_db_file_path: str,
                                                   db_temp_file_ready_for_processing_event: threading.Event):
    shutil.copy(TEST_VOCAB_DB_FILE, temp_db_file_path)
    db_update_ready_event = threading.Event()
    db_update_ready_event.set()
    db_update_processed_event = threading.Event()
    db_update_processed_event.set()
    # TODO figure out good practice for optional method parameters and the add word lookups method
    test_util.add_word_lookups_to_db_for_non_main_thread(temp_db_file_path, db_update_ready_event,
                                                         db_update_processed_event,
                                                         threading.Event())
    db_temp_file_ready_for_processing_event.set()
    logger.info(
        f"Kindle directory created and test vocab.db copied to {temp_db_file_path} (simulated mount and db update)")


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
        db_temp_file_ready_for_processing_event.clear()  # unset the event after first process
