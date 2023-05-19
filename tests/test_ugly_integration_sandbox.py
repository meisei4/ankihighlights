import os
import time
import sqlite3

import pytest

import ankiconnect_wrapper
from .. import ankikindle # TODO find out why the pycharm allows for the incorrect semantics of "import ankikindle"
from .conftest import logger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


@pytest.mark.skip("not yet")
def test_continuous_running_until_manual_exit_mount_and_unmount_with_db_processing():
    watch_for_kindle_mount_nonflask(ankikindle, ankiconnect_wrapper, "/Volumes", "Kindle")


def watch_for_kindle_mount_nonflask(ankikindle_injection: ankikindle,
                                    ankiconnect_injection: ankiconnect_wrapper,
                                    mount_dir_root: str,
                                    kindle_device_name: str):
    logger.info('Starting Kindle mounting watcher...')
    observer = Observer()

    class KindleEventHandler(FileSystemEventHandler):
        def __init__(self):
            self.directories = set(os.listdir(mount_dir_root))

        def on_modified(self, event):
            new_directories = set(os.listdir(mount_dir_root))
            added = new_directories - self.directories
            removed = self.directories - new_directories
            for directory in added:
                if directory == kindle_device_name:
                    logger.info(f"A new device '{directory}' has been mounted.")
                    handle_kindle_mount(ankikindle_injection, ankiconnect_injection, mount_dir_root, kindle_device_name)

            for directory in removed:
                if directory == kindle_device_name:
                    logger.info(f"The device '{directory}' has been unmounted.")
                    handle_kindle_unmount(kindle_device_name)

            self.directories = new_directories

    event_handler = KindleEventHandler()
    observer.schedule(event_handler, mount_dir_root, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt received, stopping observer...')
        observer.stop()

    observer.join()


def handle_kindle_mount(ankikindle_injection: ankikindle,
                        ankiconnect_injection: ankiconnect_wrapper,
                        mount_dir_root: str,
                        kindle_device_name: str):
    logger.info('Checking for Kindle mount...')
    vocab_db_path = os.path.join(mount_dir_root, kindle_device_name, 'system', 'vocabulary', 'vocab.db')
    time.sleep(1)  # Give some time for the filesystem to settle.
    for _ in range(10):  # Retry a few times in case the DB isn't ready yet.
        if os.path.exists(vocab_db_path):
            try:
                connection = sqlite3.connect(vocab_db_path)
                logger.info(f'{kindle_device_name} mounted')
                try:
                    ankikindle_injection.process_new_vocab_highlights(connection, ankiconnect_injection)
                finally:
                    connection.close()
                return True  # mounted
            except sqlite3.Error as e:
                logger.error(f'Error occurred while trying to connect to vocab.db: {e.args[0]}')
        time.sleep(1)

    logger.info('Unable to connect to vocab.db after several attempts.')
    return False  # not mounted


def handle_kindle_unmount(kindle_device_name):
    logger.info(f'{kindle_device_name} unmounted')
