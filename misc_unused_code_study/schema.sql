
 NEW SCHEMA

+------------------+      +----------------+      +----------------+
|  book_info       |      |     quotes     |      |      words     |
|----------------  | (1:N)|----------------|      |----------------|
| - id (PK)        |<-----| - id (PK)      |      | - id (PK)      |
| - asin (Unique)  |      | - book_id (FK) |      | - word         |
| - title          |      | - quote        |      | - ptntl_reading|
| - author_id (FK) |      | - timestamp    |      +----------------+
| - book_cover_file |      +----------------+           ^
| - publish_date   |             ^                     |
+------------------+             |        (N:N)        |
        | (N:1)                  +---------+-----------+
        v                                  |
+------------------+               +-------------------+
| authors          |               | quote_word        |
|------------------|               | relationship      |
| - author_id (PK) |               |-------------------|
| - name           |               | - quote_id (FK)   |
+------------------+               | - word_id (FK)    |
                                   +-------------------+

-- Book Information Table
CREATE TABLE book_info (
  id TEXT PRIMARY KEY,
  asin TEXT UNIQUE,           -- ASIN: Unique identifier for books
  title TEXT,                 -- Title of the book
  author_id TEXT REFERENCES authors(id),
  book_cover_file TEXT,       -- File path or URL for the book cover
  publish_date DATE           -- Publish date of the book
);

-- Authors Table
CREATE TABLE authors (
  author_id TEXT PRIMARY KEY,
  name TEXT,                  -- Name of the author
);

-- Words Table
CREATE TABLE words (
  id TEXT PRIMARY KEY,
  word TEXT,                  -- The word itself
  ptntl_reading TEXT          -- potential reading of the word
);

-- Quotes Table
CREATE TABLE quotes (
  id TEXT PRIMARY KEY,
  book_id TEXT REFERENCES book_info(id),  -- Foreign key to the BOOK_INFO table
  quote TEXT,                              -- Text of the quote
  timestamp BIGINT                        -- Unix Timestamp of when the quote was recorded
);

-- words <-> quotes relationship table
CREATE TABLE quote_word_relationship (
  quote_id TEXT REFERENCES quotes(id),   -- Foreign key to the QUOTES table
  word_id TEXT REFERENCES words(id),     -- Foreign key to the WORDS table
  PRIMARY KEY (quote_id, word_id)        -- Composite primary key
);
