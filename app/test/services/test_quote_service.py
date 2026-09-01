from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.repositories.quote_repository import UnknownProductIdError
from app.schemas.quote import Applicant, QuoteCreate
from app.services.quote_service import QuoteService


def _service_with_mock_repo() -> QuoteService:
    service = QuoteService()
    service.quote_repository = MagicMock()
    return service


def _quote_create() -> QuoteCreate:
    return QuoteCreate(
        product_id=1,
        applicant=Applicant(
            applicant_id=1,
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            phone="1234567890",
            date_of_birth=date(1990, 1, 1),
        ),
    )


def test_get_by_id_raises_404_when_missing():
    service = _service_with_mock_repo()
    service.quote_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_by_id("QNOPE")

    assert exc.value.status_code == 404


def test_get_by_id_returns_quote_when_found():
    service = _service_with_mock_repo()
    quote = {"id": "Q001", "status": "New"}
    service.quote_repository.get_by_id.return_value = quote

    assert service.get_by_id("Q001") == quote


def test_create_quote_generates_sequential_id_from_existing_count():
    service = _service_with_mock_repo()
    service.quote_repository.get_quotes.return_value = [{"id": "Q001"}, {"id": "Q002"}]
    service.quote_repository.save_quote.return_value = {"id": "Q003"}

    service.create_quote(_quote_create())

    saved_document = service.quote_repository.save_quote.call_args[0][0]
    assert saved_document["id"] == "Q003"
    assert saved_document["status"] == "New"
    assert saved_document["product_id"] == 1


def test_create_quote_does_not_catch_unknown_product_id_error():
    """UnknownProductIdError is now handled globally
    (app/api/exception_handlers.py), not in the service — this test guards
    that regression."""
    service = _service_with_mock_repo()
    service.quote_repository.get_quotes.return_value = []
    service.quote_repository.save_quote.side_effect = UnknownProductIdError(999)

    with pytest.raises(UnknownProductIdError):
        service.create_quote(_quote_create())


def test_update_quote_raises_404_when_missing():
    service = _service_with_mock_repo()
    service.quote_repository.update_quote.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.update_quote("QNOPE", _quote_create())

    assert exc.value.status_code == 404


def test_update_quote_does_not_catch_unknown_product_id_error():
    service = _service_with_mock_repo()
    service.quote_repository.update_quote.side_effect = UnknownProductIdError(999)

    with pytest.raises(UnknownProductIdError):
        service.update_quote("Q001", _quote_create())


def test_delete_quote_raises_404_when_missing():
    service = _service_with_mock_repo()
    service.quote_repository.delete_quote.return_value = False

    with pytest.raises(HTTPException) as exc:
        service.delete_quote("QNOPE")

    assert exc.value.status_code == 404


def test_get_by_page_sets_next_cursor_when_has_more():
    service = _service_with_mock_repo()
    items = [{"id": "Q001"}, {"id": "Q002"}]
    service.quote_repository.get_by_cursor.return_value = (items, True)

    result = service.get_by_page(after=None, limit=2)

    assert result == {"data": items, "next_cursor": "Q002", "has_more": True}


def test_get_by_page_sets_next_cursor_none_when_no_more():
    service = _service_with_mock_repo()
    items = [{"id": "Q099"}]
    service.quote_repository.get_by_cursor.return_value = (items, False)

    result = service.get_by_page(after="Q098", limit=10)

    assert result == {"data": items, "next_cursor": None, "has_more": False}
