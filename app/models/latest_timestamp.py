from sqlalchemy import Column, Integer, BigInteger

from app.models.meta import Base


class LatestTimestamp(Base):
    __tablename__ = 'latest_timestamp'
    id = Column(Integer, primary_key=True)
    timestamp = Column(BigInteger, nullable=False)

