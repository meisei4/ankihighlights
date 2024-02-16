import sqlite3
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.models.models import Word, BookInfo, Lookup

# TODO: figure out if this should become a CLI implementation
class KindleSyncService:
    @staticmethod
    def sync_from_kindle_db(kindle_db_path):
        # Connect to the Kindle database
        with sqlite3.connect(kindle_db_path) as kindle_conn:
            kindle_cursor = kindle_conn.cursor()

            # Extract data from Kindle DB
            kindle_cursor.execute("""
                SELECT w.word, l.usage, l.timestamp, b.title, b.authors 
                FROM lookups l
                INNER JOIN words w ON l.word_key = w.id
                INNER JOIN book_info b ON l.book_key = b.id
            """)
            rows = kindle_cursor.fetchall()

            for row in rows:
                KindleSyncService.process_row(row)

    @staticmethod
    def process_row(row):
        word_text, usage_text, timestamp, book_title, book_authors = row

        # Transform and load data into Custom DB
        try:
            # Handling Word
            word = Word.query.filter_by(word=word_text).first()
            if not word:
                word = Word(word=word_text)
                db.session.add(word)
                db.session.flush()  # Generates the ID for further use

            # Handling BookInfo
            book_info = BookInfo.query.filter_by(title=book_title, authors=book_authors).first()
            if not book_info:
                book_info = BookInfo(title=book_title, authors=book_authors)
                db.session.add(book_info)
                db.session.flush()  # Generates the ID for further use

            # Handling Lookup
            # Convert timestamp from Kindle's format to POSIX timestamp
            usage_timestamp = timestamp  # Adjust transformation as necessary
            lookup = Lookup.query.filter_by(word_id=word.id, book_info_id=book_info.id, usage=usage_text).first()
            if not lookup:
                lookup = Lookup(word_id=word.id, book_info_id=book_info.id, usage=usage_text, timestamp=usage_timestamp)
                db.session.add(lookup)

            db.session.commit()

        except SQLAlchemyError as e:
            db.session.rollback()
            # Proper logging is essential for debugging
            print(f"Error processing row {row}: {e}")

# Use the service
kindle_db_path = 'path_to_kindle_db.sqlite'
KindleSyncService.sync_from_kindle_db(kindle_db_path)
