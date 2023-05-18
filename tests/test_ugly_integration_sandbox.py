import os
import time
import sqlite3
import ankikindle
import ankiconnect_wrapper
from .conftest import logger
from watchdog.observers import Observer
from watchdog.events import DirCreatedEvent, DirDeletedEvent


# TODO this is the ugly physical mount and monitor the log with your eyes test ewww
def test_continuous_until_manual_exit_mount_and_unmount_with_db_processing():
    watch_for_kindle_mount_nonflask(ankikindle, ankiconnect_wrapper, "/Volumes", "Kindle")


def handle_mount_event(ankikindle_injection, ankiconnect_injection, kindle_device_name, mounted, event):
    if isinstance(event, DirCreatedEvent):
        return handle_kindle_mount(ankikindle_injection, ankiconnect_injection, kindle_device_name, event)
    elif isinstance(event, DirDeletedEvent):
        return handle_kindle_unmount(kindle_device_name, mounted, event)
    else:
        return mounted


def handle_kindle_mount(ankikindle_injection, ankiconnect_injection, kindle_device_name, event):
    if os.path.basename(event.src_path) != kindle_device_name:
        return False

    vocab_db_path = os.path.join(event.src_path, 'system', 'vocabulary', 'vocab.db')
    time.sleep(1)  # allow some time for the filesystem to settle

    for _ in range(10):  # retry a few times in case the DB isn't ready yet
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
                logger.error(f"An error occurred: {e.args[0]}")
        time.sleep(1)

    return False  # not mounted


def handle_kindle_unmount(kindle_device_name, mounted, event):
    if os.path.basename(event.src_path) == kindle_device_name and mounted:
        logger.info(f'{kindle_device_name} unmounted')
        return False  # not mounted

    return mounted


def watch_for_kindle_mount_nonflask(ankikindle_injection, ankiconnect_injection, mount_dir_root, kindle_device_name):
    observer = Observer()
    mounted = False

    def event_handler(event):
        nonlocal mounted
        mounted = handle_mount_event(ankikindle_injection, ankiconnect_injection, kindle_device_name, mounted, event)

    observer.schedule(event_handler, mount_dir_root, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)  # keep the script running
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
