Here is the markdown file reflecting the current models and including the Kindle references:

```markdown
# SQLite Kindle Database to PostgreSQL Custom Database Typing Mapping

## Mapping Overview

This document provides a detailed mapping of how the data from the Kindle's SQLite database (`vocab.db`) is translated and stored into the PostgreSQL custom database used by the Flask application.

### SQLite Kindle Database

- `BOOK_INFO`
  - `id`: TEXT NOT NULL (Not directly used in Custom)
  - `asin`: TEXT (Not used in Custom)
  - `guid`: TEXT (Not used in Custom)
  - `lang`: TEXT (Not used in Custom)
  - `title`: TEXT (Mapped to `title: VARCHAR(255) NOT NULL` in Custom)
  - `authors`: TEXT (Mapped to `authors: VARCHAR(255) NOT NULL` in Custom)

- `DICT_INFO`
  - Not used in Custom

- `LOOKUPS`
  - `id`: TEXT NOT NULL (Not directly used in Custom)
  - `word_key`: TEXT (Mapped to `word_id: INTEGER` in Custom, References `words(id)`)
  - `book_key`: TEXT (Mapped to `book_id: INTEGER` in Custom, References `book_info(id)`)
  - `dict_key`: TEXT (Not used in Custom)
  - `pos`: TEXT (Not used in Custom)
  - `usage`: TEXT (Mapped to `usage: VARCHAR(255) NOT NULL` in Custom)
  - `timestamp`: INTEGER DEFAULT 0 (Mapped to `timestamp: BIGINT NOT NULL` in Custom)

- `WORDS`
  - `id`: TEXT NOT NULL (Not directly used in Custom)
  - `word`: TEXT (Mapped to `word: VARCHAR(255) NOT NULL UNIQUE` in Custom)
  - `stem`: TEXT (Not used in Custom)
  - `lang`: TEXT (Not used in Custom)

## PostgreSQL Custom Database Models

- `LATEST_TIMESTAMP`
  - `id`: INTEGER PRIMARY KEY (Custom)
  - `timestamp`: BIGINT NOT NULL (Mapped from `timestamp: INTEGER DEFAULT 0` in Kindle)

- `ANKI_CARDS`
  - `id`: INTEGER PRIMARY KEY (Custom)
  - `word_id`: INTEGER (References `words(id)` in Custom)
  - `deck_name`: VARCHAR(255) NOT NULL (Custom)
  - `model_name`: VARCHAR(255) NOT NULL (Custom)
  - `front`: VARCHAR(255) NOT NULL (Custom)
  - `back`: VARCHAR(255) NOT NULL (Custom)
  - `anki_card_id`: VARCHAR(255) NOT NULL UNIQUE (Custom)
  - `usage`: VARCHAR(255) (Custom)
  - `timestamp`: BIGINT NOT NULL (Mapped from `timestamp: INTEGER DEFAULT 0` in Kindle)
