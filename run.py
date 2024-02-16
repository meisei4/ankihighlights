from app import create_app, db
from app.services.kindle_db_sync_service import KindleSyncService
import os

app = create_app()


def sync_kindle_db():
    kindle_db_path = os.getenv('KINDLE_DB_PATH')
    if kindle_db_path:
        with app.app_context():
            KindleSyncService.sync_from_kindle_db(kindle_db_path)


if __name__ == "__main__":
    if os.getenv('FLASK_ENV') == 'development':
        sync_kindle_db()
    app.run(host='0.0.0.0', port=int(os.getenv('FLASK_RUN_PORT', 5000)),
            debug=os.getenv('FLASK_DEBUG', False) == 'True')
