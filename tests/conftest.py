from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
import os

postgres_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/fm_ims_test"

os.environ["FM_POSTGRES_URL"] = postgres_url


@pytest.fixture(scope="session")
def postgres_fixture():
    # Create an async SQLAlchemy engine
    pg_url = str(postgres_url).split("asyncpg")

    engine = create_engine(url="postgresql+psycopg2" + pg_url[-1], echo=True)
    from fm_inventory.utils.abstract_base import AbstractBase
    from fm_inventory.app import app

    # Create all tables
    AbstractBase.metadata.create_all(bind=engine)

    yield

    # Drop all tables after all tests
    AbstractBase.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def app_test_client_fixture(postgres_fixture):
    from fm_inventory.app import app

    with TestClient(app=app) as test_client:
        yield test_client
