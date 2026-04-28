import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Connection, Transaction
from typing import Generator
from fastapi.testclient import TestClient

from travel_agency_backend.config.settings import settings
from travel_agency_backend.models import Base
from travel_agency_backend.main import app
from travel_agency_backend.db.session import get_session

engine = create_engine(settings.test_database_url)
TestingSessionFactory = sessionmaker(bind=engine, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_connection() -> Generator[Connection, None, None]:
    connection = engine.connect()
    transaction = connection.begin()

    yield connection

    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def db_session(db_connection: Connection) -> Generator[Session, None, None]:
    session = TestingSessionFactory(bind=db_connection)

    # SAVEPOINT for nested transactions
    nested = db_connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session_: Session, transaction_: Transaction):
        nonlocal nested

        if transaction_.nested and not transaction_._parent_nested:
            nested = db_connection.begin_nested()

    yield session

    session.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
