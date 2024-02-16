import sqlite3
from datetime import datetime
from app import db
from app.models.models import Word, BookInfo, Lookup

class KindleSyncService:
    @staticmethod
    def sync_from_kindle_db(kindle_db_path):
        # Connect to the Kindle database
        kindle_conn = sqlite3.connect(kindle_db_path)
        kindle_cursor = kindle_conn.cursor()

        # Assuming the Kindle DB has tables for words, usage, and book information
        # Adjust SQL based on actual Kindle DB structure
        kindle_cursor.execute("""
            SELECT w.word, l.usage, l.timestamp, b.title, b.authors 
            FROM lookups l
            JOIN words w ON l.word_id = w.id
            JOIN books b ON l.book_id = b.id
        """)
        rows = kindle_cursor.fetchall()

        for row in rows:
            KindleSyncService.process_row(row)

        kindle_conn.close()

    @staticmethod
    def process_row(row):
        word_text, usage_text, timestamp, book_title, book_authors = row

        # Handling Word
        word = Word.query.filter_by(word=word_text).first()
        if not word:
            word = Word(word=word_text)
            db.session.add(word)

        # Handling BookInfo
        book_info = BookInfo.query.filter_by(title=book_title, authors=book_authors).first()
        if not book_info:
            book_info = BookInfo(title=book_title, authors=book_authors)
            db.session.add(book_info)

        # Handling Lookup
        # Convert timestamp if necessary
        usage_timestamp = datetime.fromtimestamp(timestamp)
        lookup = Lookup.query.filter_by(word_id=word.id, book_info_id=book_info.id, usage=usage_text, timestamp=usage_timestamp).first()
        if not lookup:
            lookup = Lookup(word=word, book_info=book_info, usage=usage_text, timestamp=usage_timestamp)
            db.session.add(lookup)

        db.session.commit()
