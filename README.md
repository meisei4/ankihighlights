# README: ankikindle 

ankikindle is a Python project that integrates Kindle vocabulary highlights with the Anki flashcard system. This project scans for new vocabulary highlights, processes them, and automatically adds them to a specified Anki deck as flashcards. The project utilizes the AnkiConnect API to interact with Anki.

## Table of Contents

- [Features](#features)
- [Database Structure](#database-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

## Features

- Automatically processes new vocabulary highlights
- Adds new flashcards to a specified Anki deck
- Updates existing flashcards with additional example sentences (upon duplicate highlights/lookups to kindle vocab db)
- Supports custom deck and card type configurations (not yet)
- Provides a priority deck for frequent vocabulary (vocab words that are encountered more than a certain threshold while reading on kindle)


## Database Structure

The database used in this script is an SQLite database containing the following tables (these are the only important ones):

1. `LOOKUPS`
2. `WORDS`
3. `BOOK_INFO`
4. `latest_timestamp` --this table is actually added during the running on the app in order to keep track of user's latest_timestamp for a highlight

### Table: LOOKUPS

| Column     | Data Type |
|------------|-----------|
| id         | INTEGER   |
| word_key   | INTEGER   |
| book_key   | INTEGER   |
| usage      | TEXT      |
| timestamp  | INTEGER   |

### Table: WORDS

| Column     | Data Type |
|------------|-----------|
| id         | INTEGER   |
| word       | TEXT      |

### Table: BOOK_INFO

| Column     | Data Type |
|------------|-----------|
| id         | INTEGER   |
| title      | TEXT      |
| authors    | TEXT      |

### Table: latest_timestamp

| Column     | Data Type |
|------------|-----------|
| id         | INTEGER   |
| timestamp  | INTEGER   |



## Installation

1. Ensure you have Python 3.8 or higher installed on your system.
2. Install the required packages (so far):

```bash
pip install requests pytest flask selenium
```

1. Install the AnkiConnect add-on in Anki by following the instructions on [anki-connect's GitHub page](https://github.com/FooSoft/anki-connect).

## Usage

1. Start the Anki application and ensure the AnkiConnect add-on is running.

2. This project includes two main test modules: `test_ankikindle.py` and `test_vocab_db_wrapper.py`.

### Test Module: test_ankikindle.py

The `test_ankikindle.py` module tests the main functionality of the ankikindle script (recognizing listesned to DB updates, creating and or updating cards). Some tests include:

1. `test_update_database_while_main_program_is_running(main_thread_test_db_connection: Connection)`: Tests whether the database is updated correctly while the main program is running.
2. `ankikindle_main_function_wrapper(connection_injection: Connection, ankiconnect_injection: ankiconnect_wrapper, db_update_ready_event: threading.Event, db_update_processed_event: threading.Event, stop_event: threading.Event)`: Wraps the main Ankikindle function for testing purposes.
3. `test_add_update_and_remove_notes_to_anki()`: Tests adding, updating, and removing notes in Anki.

### Test Module: test_vocab_db_wrapper.py

The `test_vocab_db_wrapper.py` module tests the functions related to the vocabulary database. Some tests include:

1. `test_get_all_word_look_ups_after_timestamp(main_thread_test_db_connection: Connection)`: Tests whether all word lookups after a specific timestamp are retrieved correctly.
2. `add_word_lookups_to_db(db_update_ready_event: threading.Event, db_update_processed_event: threading.Event, stop_event: threading.Event)`: Adds word lookups to the test database.


## Contributing

Contributions are welcome! Please submit a pull request or create an issue if you have suggestions for improvements or bug fixes.
