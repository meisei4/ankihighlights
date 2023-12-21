+------------------+     +------------------+     +------------------+
|    BOOK_INFO     |     |      USAGES      |     |      WORDS       |
|------------------|(1:N)|------------------|     |------------------|
| - id (PK)        |<----| - book_id (FK)   |(N:1)| - id (PK)        |
| - asin (Unique)  |     | - word_id (FK)   |---->| - word           |
| - title          |     | - id (PK)        |     | - stem           |
| - authors        |     | - usage          |     | - timestamp      |
+------------------+     | - timestamp      |     +------------------+
                         +------------------+
Cardinatility:
BOOK_INFO <- USAGES one-to-many
USAGES -> WORDS many-to-one

CREATE TABLE book_info (
  id TEXT PRIMARY KEY,
  asin TEXT UNIQUE,           -- ASIN is standardized unique identifier for books (maybe this is the primary key?)
  title TEXT,                 -- Title of the book
  authors TEXT                -- Authors of the book
);

CREATE TABLE words (
  id TEXT PRIMARY KEY,
  word TEXT,                  -- The word itself
  stem TEXT                   -- The stem of the word (furigana)
);

CREATE TABLE usages (
  id TEXT PRIMARY KEY,
  usage TEXT,                 -- Example sentence containing usage of a specific word
  word_id TEXT REFERENCES words(id),   -- Foreign key to the WORDS table
  book_id TEXT REFERENCES book_info(id), -- Foreign key to the BOOK_INFO table
  timestamp BIGINT            -- unix Timestamp of when the usage was found (not sure if this is bigint or not)
);

