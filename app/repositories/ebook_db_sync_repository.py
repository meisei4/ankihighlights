
from app.models.book_info import BookInfo
from app.models.lookup import Lookup
from app.models.meta import DBSession
from app.models.word import Word
from app.logger import logger


class EbookDBSyncRepository:
    def get_word(self, word_text):
        return DBSession.query(Word).filter_by(word=word_text).first()

    def add_word(self, word):
        DBSession.add(word)
        DBSession.flush()  # Generates the ID for further use

    def get_book_info(self, title, authors):
        return DBSession.query(BookInfo).filter_by(title=title, authors=authors).first()

    def add_book_info(self, book_info):
        DBSession.add(book_info)
        DBSession.flush()  # Generates the ID for further use

    def get_lookup(self, word_id, book_id, usage_text):
        return DBSession.query(Lookup).filter_by(word_id=word_id, book_id=book_id, usage=usage_text).first()

    def add_lookup(self, lookup):
        DBSession.add(lookup)

    def commit(self):
        DBSession.commit()

    def rollback(self):
        DBSession.rollback()

    def fetch_all_rows(self, ebook_vocab_db_conn):
        with ebook_vocab_db_conn:
            ebook_db_cursor = ebook_vocab_db_conn.cursor()
            ebook_db_cursor.execute("""
                SELECT w.word, l.usage, l.timestamp, b.title, b.authors 
                FROM lookups l
                INNER JOIN words w ON l.word_key = w.id
                INNER JOIN book_info b ON l.book_key = b.id
            """)
            return ebook_db_cursor.fetchall()
