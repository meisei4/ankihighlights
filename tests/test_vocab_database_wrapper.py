import json
import os
import shutil

import vocab_database_wrapper
import sqlite3


# TODO figure out the remote db thing, and how to have that be reflected


def test_copy_to_backup_and_tmp_infinitely():
    vocab_database_wrapper.copy_to_backup_and_tmp_infinitely()
    shutil.rmtree(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backup')))


def test_get_table_info():
    # __file__ is this file__, so next command is: get path to this module file, hop out with cd .., then go cd
    # resource, then there's the file
    test_vocab_db_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'vocab.db'))
    db_connection = sqlite3.connect(test_vocab_db_file)
    table_info = vocab_database_wrapper.get_table_info(db_connection)
    print(json.dumps(table_info, indent=2))
    assert table_info is not None
