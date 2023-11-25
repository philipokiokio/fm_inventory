from fm_inventory.config import Settings
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base


settings = Settings()

metadata = MetaData()

Base = declarative_base(metadata=metadata)


engine = create_async_engine(url=str(settings.postgres_url))

async_session = async_sessionmaker(engine, expire_on_commit=False)
