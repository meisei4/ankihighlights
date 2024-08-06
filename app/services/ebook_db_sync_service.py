from app.logger import logger
from app.models.word import Word
from app.models.book_info import BookInfo
from app.models.lookup import Lookup
from app.repositories.ebook_db_sync_repository import EbookDBSyncRepository
from sqlalchemy.exc import SQLAlchemyError
from injector import inject


class EbookDBSyncService:
    @inject
    def __init__(self, repository: EbookDBSyncRepository):
        self.repository = repository

    def sync_from_ebook_db(self, ebook_vocab_db_conn):
        logger.info(f"Starting sync from ebook database")
        try:
            rows = self.repository.fetch_all_rows(ebook_vocab_db_conn)
            logger.info(f"Retrieved {len(rows)} rows from ebook database")

            for row in rows:
                self.process_row(row)
            logger.info("Sync completed successfully.")
        except Exception as e:
            logger.error(f"Error during sync: {e}")

    def process_row(self, row):
        word_text, usage_text, timestamp, book_title, book_authors = row
        logger.debug(f"Processing row: {row}")

        try:
            word = self.repository.get_word(word_text)
            if not word:
                word = Word(word=word_text)
                self.repository.add_word(word)

            book_info = self.repository.get_book_info(book_title, book_authors)
            if not book_info:
                book_info = BookInfo(title=book_title, authors=book_authors)
                self.repository.add_book_info(book_info)

            usage_timestamp = timestamp
            lookup = self.repository.get_lookup(word.id, book_info.id, usage_text)
            if not lookup:
                lookup = Lookup(word_id=word.id, book_id=book_info.id, usage=usage_text, timestamp=usage_timestamp)
                self.repository.add_lookup(lookup)

            self.repository.commit()
            logger.info(f"Successfully processed and inserted/updated row in the database for word: {word_text}")

        except SQLAlchemyError as e:
            self.repository.rollback()
            logger.error(f"Error processing row {row}: {e}")
