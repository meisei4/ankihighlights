from app.models.latest_timestamp import LatestTimestamp

class LatestTimestampDTO:
    @staticmethod
    def to_dict(latest_timestamp: LatestTimestamp) -> dict:
        return {
            'id': latest_timestamp.id,
            'timestamp': latest_timestamp.timestamp,
        }

    @staticmethod
    def from_dict(data: dict) -> LatestTimestamp:
        return LatestTimestamp(
            id=data.get('id'),
            timestamp=data.get('timestamp')
        )
