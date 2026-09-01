from unittest.mock import patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.api.exception_handlers import register_exception_handler
from app.api.routes.quotes_router import router as quotes_router
from app.repositories.quote_repository import UnknownProductIdError


@pytest.fixture
def client():
    app = FastAPI()
    register_exception_handler(app)
    app.include_router(quotes_router)
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def mock_service():
    with patch("app.api.routes.quotes_router.QuoteService") as mock_cls:
        yield mock_cls.return_value


def _applicant_json():
    return {
        "applicant_id": 1,
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "phone": "1234567890",
        "date_of_birth": "1990-01-01",
    }


def _quote_json(quote_id="Q001"):
    return {
        "id": quote_id,
        "status": "New",
        "product_id": 1,
        "applicant": _applicant_json(),
        "question_set": [],
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }


def test_get_quotes_returns_list(client, mock_service):
    mock_service.get_quotes.return_value = [_quote_json()]

    response = client.get("/quotes/")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_quotes_passes_query_params(client, mock_service):
    mock_service.search_quotes.return_value = [_quote_json()]

    response = client.get("/quotes/search?name=Jane&category=Audi")

    assert response.status_code == 200
    mock_service.search_quotes.assert_called_once_with(name="Jane", category="Audi")


def test_search_route_not_swallowed_by_quote_id_route(client, mock_service):
    """Regression guard: /quotes/search must be registered before
    /quotes/{quote_id}, otherwise it'd be captured as quote_id='search'."""
    mock_service.search_quotes.return_value = []

    response = client.get("/quotes/search")

    assert response.status_code == 200
    mock_service.get_by_id.assert_not_called()


def test_get_by_page_returns_envelope(client, mock_service):
    mock_service.get_by_page.return_value = {
        "data": [_quote_json()], "next_cursor": "Q001", "has_more": True
    }

    response = client.get("/quotes/page?limit=10")

    assert response.status_code == 200
    assert response.json()["has_more"] is True
    mock_service.get_by_page.assert_called_once_with(None, 10)


def test_page_route_not_swallowed_by_quote_id_route(client, mock_service):
    mock_service.get_by_page.return_value = {"data": [], "next_cursor": None, "has_more": False}

    response = client.get("/quotes/page")

    assert response.status_code == 200
    mock_service.get_by_id.assert_not_called()


def test_get_by_page_rejects_limit_out_of_bounds(client, mock_service):
    assert client.get("/quotes/page?limit=0").status_code == 422
    assert client.get("/quotes/page?limit=51").status_code == 422


def test_get_by_id_returns_quote(client, mock_service):
    mock_service.get_by_id.return_value = _quote_json()

    response = client.get("/quotes/Q001")

    assert response.status_code == 200
    mock_service.get_by_id.assert_called_once_with("Q001")


def test_get_by_id_propagates_404_from_service(client, mock_service):
    mock_service.get_by_id.side_effect = HTTPException(status_code=404, detail="Quote not found")

    response = client.get("/quotes/QNOPE")

    assert response.status_code == 404


def test_create_quote_returns_201(client, mock_service):
    mock_service.create_quote.return_value = _quote_json()

    response = client.post("/quotes/", json={"product_id": 1, "applicant": _applicant_json()})

    assert response.status_code == 201


def test_create_quote_rejects_invalid_body(client, mock_service):
    response = client.post("/quotes/", json={"product_id": 1})

    assert response.status_code == 422
    mock_service.create_quote.assert_not_called()


def test_create_quote_returns_404_via_global_handler_on_unknown_product(client, mock_service):
    mock_service.create_quote.side_effect = UnknownProductIdError(999)

    response = client.post("/quotes/", json={"product_id": 999, "applicant": _applicant_json()})

    assert response.status_code == 404
    assert response.json() == {"detail": "Unknown product_id: 999"}


def test_update_quote_returns_200(client, mock_service):
    mock_service.update_quote.return_value = _quote_json()

    response = client.put("/quotes/Q001", json={"product_id": 1, "applicant": _applicant_json()})

    assert response.status_code == 200


def test_delete_quote_returns_204(client, mock_service):
    mock_service.delete_quote.return_value = None

    response = client.delete("/quotes/Q001")

    assert response.status_code == 204
    mock_service.delete_quote.assert_called_once_with("Q001")
