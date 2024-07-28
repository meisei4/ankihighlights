import os
import sqlite3

from app.app import create_app
from app.services.ebook_db_sync_service import EbookDBSyncService
from config import load_environment

load_environment()

app = create_app()


def sync_ebook_db():
    ebook_db_env_path = os.getenv('FLASK_INTEGRATION_DB_PATH')
    ebook_db_abs_path = os.path.abspath(
        ebook_db_env_path)  # TODO figure out how to make this kind of stuff consistent...
    with app.app_context():
        ebook_vocab_db_conn = sqlite3.connect(ebook_db_abs_path)
        EbookDBSyncService.sync_from_ebook_db(ebook_vocab_db_conn)


if __name__ == "__main__":
    # sync_ebook_db()

    app.run(host='0.0.0.0', port=int(os.getenv('FLASK_RUN_PORT')))
