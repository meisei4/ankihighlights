# README: ankikindle

### Overview

This application is a Flask-based web app that integrates with SQLite to access the Kindle's vocabulary database,
extracts words and their usage, and uses AnkiConnect to add these words to an Anki deck. The Kindle's vocabulary
database is a SQLite file named `vocab.db` (e.g., for macOS located at the system
path `/Volumes/Kindle/system/vocabulary/vocab.db` when the Kindle device is mounted).

The `vocab.db` database consists of several tables, with the `LOOKUPS` and `WORDS` tables being the most relevant.
The `LOOKUPS` table contains the word usage and its metadata, while the `WORDS` table contains the words themselves.

## Table of Contents

- [Features](#features)
- [Limitations](#limitations)
- [Database Structure](#database-structure)
- [Installation](#installation)
- [Usage](#usage)

## Features

- Automatically processes new vocabulary highlights.
- Adds new flashcards to a specified Anki deck.
- Updates existing flashcards with additional example sentences (upon duplicate highlights/lookups to Kindle vocab db).
- Supports custom deck and card type configurations (not yet implemented).
- Provides a priority deck for frequent vocabulary (vocab words that are encountered more than a certain threshold while
  reading on Kindle).

## Database Structure

For details, see the `models.py` module and this file: [schema_synch.md](misc%2Fschema_synch.md)

## Installation

It is recommended to use PyCharm Community Edition and set up a Poetry virtual environment.

1. Install the necessary dependencies:

   ```bash
   poetry install
   ```

2. Install the AnkiConnect add-on in Anki by following the instructions
   on [anki-connect's GitHub page](https://github.com/FooSoft/anki-connect).

## Usage

1. Start the Anki application and ensure the AnkiConnect add-on is running.

2. Run the tests to ensure everything is set up correctly. Running the module has not been fully tested yet.