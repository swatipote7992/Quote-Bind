import pytest
from sqlalchemy.orm import Session

from app.api.dependencies import get_db


def test_get_db_yields_a_session():
    generator = get_db()

    db = next(generator)

    assert isinstance(db, Session)
    generator.close()  # runs the `finally: db.close()` without needing StopIteration


def test_get_db_closes_session_when_generator_exhausted():
    generator = get_db()
    next(generator)

    with pytest.raises(StopIteration):
        next(generator)
