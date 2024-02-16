from app import create_app
from app.services.kindle_db_sync_service import KindleSyncService
import os

# Initialize the Flask application
app = create_app()


def sync_kindle_db():

    kindle_db_path = os.getenv('KINDLE_DB_PATH')
    if kindle_db_path:
        with app.app_context():
            KindleSyncService.sync_from_kindle_db(kindle_db_path)


if __name__ == "__main__":
    # TODO: figure out how to better integrate the syncing
    sync_kindle_db()

    # Start the Flask application
    app.run(host='0.0.0.0', port=int(os.getenv('FLASK_RUN_PORT', 5000)))
