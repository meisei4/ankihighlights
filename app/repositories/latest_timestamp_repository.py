from app.models.latest_timestamp import LatestTimestamp
from app.models.meta import DBSession


class LatestTimestampRepository:
    def get_latest_timestamp(self):
        latest_timestamp_record = DBSession.query(LatestTimestamp).order_by(LatestTimestamp.timestamp.desc()).first()
        return latest_timestamp_record.timestamp if latest_timestamp_record else 0

    def set_latest_timestamp(self, timestamp):
        latest_timestamp_record = LatestTimestamp(timestamp=timestamp)
        DBSession.add(latest_timestamp_record)
        DBSession.commit()

    def check_and_create_latest_timestamp_if_not_exists(self):
        if DBSession.query(LatestTimestamp).count() == 0:
            latest_timestamp = LatestTimestamp(timestamp=0)  # Default timestamp
            DBSession.add(latest_timestamp)
            DBSession.commit()
