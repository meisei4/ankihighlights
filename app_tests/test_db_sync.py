from app.models.models import Word, BookInfo, Lookup
from app.services.kindle_db_sync_service import KindleSyncService


def test_sync_from_kindle_db(test_app, kindle_db_path):
    """Test syncing data from the Kindle database into the application's database."""
    with test_app.app_context():
        # Assuming KindleSyncService is correctly implemented to handle the path
        KindleSyncService.sync_from_kindle_db(kindle_db_path)

        # Perform assertions to verify that data has been correctly inserted
        assert Word.query.count() > 0, "Words should be inserted into the database."
        assert BookInfo.query.count() > 0, "BookInfos should be inserted into the database."
        assert Lookup.query.count() > 0, "Lookups should be inserted into the database."
