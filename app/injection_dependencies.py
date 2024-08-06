from flask_injector import inject

from app.models.dto.latest_timestamp_dto import LatestTimestampDTO
from app.models.dto.lookup_dto import LookupDTO
from app.repositories.highlight_repository import HighlightRepository
from app.repositories.latest_timestamp_repository import LatestTimestampRepository
from app.services.ebook_db_sync_service import EbookDBSyncService
from app.services.highlight_service import HighlightService


class Dependencies:
    @inject
    def __init__(self,
                 highlight_service: HighlightService,
                 latest_timestamp_dto: LatestTimestampDTO,
                 lookup_dto: LookupDTO,
                 highlight_repository: HighlightRepository,
                 latest_timestamp_repository: LatestTimestampRepository,
                 ebook_db_sync_service: EbookDBSyncService):
        self.highlight_service = highlight_service
        self.latest_timestamp_dto = latest_timestamp_dto
        self.lookup_dto = lookup_dto
        self.highlight_repository = highlight_repository
        self.latest_timestamp_repository = latest_timestamp_repository
        self.ebook_db_sync_service = ebook_db_sync_service
