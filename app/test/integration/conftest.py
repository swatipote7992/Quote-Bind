import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base
from app.models import quote_model  # noqa: F401 - ensure all models are registered on Base

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def db_session(monkeypatch):
    """Fresh in-memory SQLite DB per test. Each repository's SessionLocal is
    patched to use it instead of the real Postgres one, so repository tests
    run real SQL with no external database required."""
    Base.metadata.create_all(bind=test_engine)

    monkeypatch.setattr("app.repositories.product_repository.SessionLocal", TestSessionLocal)
    monkeypatch.setattr("app.repositories.question_repository.SessionLocal", TestSessionLocal)
    monkeypatch.setattr("app.repositories.quote_repository.SessionLocal", TestSessionLocal)

    yield TestSessionLocal

    Base.metadata.drop_all(bind=test_engine)
