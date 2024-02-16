from app import create_app
from app.services.kindle_db_sync_service import KindleSyncService

app = create_app()

if __name__ == "__main__":
    kindle_db_path = '/path/to/your/kindle/database'
    KindleSyncService.sync_from_kindle_db(kindle_db_path)
    app.run(debug=True)
