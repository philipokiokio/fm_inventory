from fm_inventory.database_conf import DeclarativeBase
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime


class AbstractBase(DeclarativeBase):
    __abstract__ = True
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    date_created_utc = Column(DateTime(), default=datetime.utcnow)
    date_updated_utc = Column(DateTime(), onupdate=datetime.utcnow)

    def as_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}
