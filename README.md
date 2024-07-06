# README: ankikindle

### How it Works

The application uses SQLite to access the Kindle's vocabulary database, extracts the words and their usage, and then
uses AnkiConnect to add these words to an Anki deck. The Kindle's vocabulary database is a SQLite file
named `vocab.db` (e.g. for macOS located at the system path `/Volumes/Kindle/system/vocabulary/vocab.db` when the Kindle
device is mounted.

The `vocab.db` database consists of several tables, among which the `LOOKUPS` and `WORDS` tables are most relevant.
The `LOOKUPS` table contains the word usage and its metadata, and the `WORDS` table contains the words.

## Table of Contents

- [Features](#features)
- [Limitations](#limitations)
- [Database Structure](#database-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

## Features

- Automatically processes new vocabulary highlights
- Adds new flashcards to a specified Anki deck
- Updates existing flashcards with additional example sentences (upon duplicate highlights/lookups to kindle vocab db)
- Supports custom deck and card type configurations (not yet)
- Provides a priority deck for frequent vocabulary (vocab words that are encountered more than a certain threshold while
  reading on kindle)

## Limitations

The application assumes that the AnkiConnect server is running on the default port, and that the SQLite database file is
located at the default path on the Kindle device. The integration test doesn't check the state of the database after
processing. Also there is not custom deck or confif yet, the plan is to use a standardized card type.

## Database Structure

The database used in this script is an SQLite database containing the following tables (these are the only important
ones):

1. `LOOKUPS`
2. `WORDS`
3. `BOOK_INFO`
4. `latest_timestamp` --this table is actually added during the running on the app in order to keep track of user's
   latest_timestamp for a highlight

### Table: LOOKUPS

| Column    | Data Type |
|-----------|-----------|
| id        | INTEGER   |
| word_key  | INTEGER   |
| book_key  | INTEGER   |
| usage     | TEXT      |
| timestamp | INTEGER   |

### Table: WORDS

| Column | Data Type |
|--------|-----------|
| id     | INTEGER   |
| word   | TEXT      |

### Table: BOOK_INFO

| Column  | Data Type |
|---------|-----------|
| id      | INTEGER   |
| title   | TEXT      |
| authors | TEXT      |

### Table: latest_timestamp

| Column    | Data Type |
|-----------|-----------|
| id        | INTEGER   |
| timestamp | INTEGER   |

## Installation

1. Ensure you have Python 3.8 or higher installed on your system.
2. Install the required packages (so far):

```bash
pip install requests pytest flask selenium watchdog
```

1. Install the AnkiConnect add-on in Anki by following the instructions
   on [anki-connect's GitHub page](https://github.com/FooSoft/anki-connect).

## Usage

1. Start the Anki application and ensure the AnkiConnect add-on is running.

2. just run the tests and stuff so far, running the module has not fully been tested

### Test Module: test_ankikindle.py

Tests include:

- Unit tests for individual functions.
- Mock tests that simulate interactions with AnkiConnect and SQLite.
- Integration test that simulates the mounting of a Kindle device, and checks the processing of the vocabulary database.

The tests also include an integration test (`test_basic_integration_with_kindle_mounting_and_db_processing`) which
simulates Kindle device mounting and vocabulary database processing.

## Contributing

Contributions are welcome! Please submit a pull request or create an issue if you have suggestions for improvements or
bug fixes.
