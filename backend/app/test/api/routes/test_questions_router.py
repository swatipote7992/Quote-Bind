from unittest.mock import patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.api.exception_handlers import register_exception_handler
from app.api.routes.questions_router import router as questions_router


@pytest.fixture
def client():
    app = FastAPI()
    register_exception_handler(app)
    app.include_router(questions_router)
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def mock_service():
    with patch("app.api.routes.questions_router.QuestionService") as mock_cls:
        yield mock_cls.return_value


def test_get_questions_returns_list(client, mock_service):
    mock_service.get_questions.return_value = [
        {"question_id": 1, "question_label": "Are you 18?", "default_answer": "Yes"}
    ]

    response = client.get("/questions/")

    assert response.status_code == 200
    assert response.json() == [
        {"question_id": 1, "question_label": "Are you 18?", "default_answer": "Yes"}
    ]


def test_get_by_page_returns_envelope(client, mock_service):
    mock_service.get_by_page.return_value = {
        "data": [{"question_id": 1, "question_label": "Q", "default_answer": "Yes"}],
        "page": 1,
        "page_size": 10,
        "total": 1,
        "total_pages": 1,
    }

    response = client.get("/questions/page?page=1&page_size=10")

    assert response.status_code == 200
    assert response.json()["total"] == 1
    mock_service.get_by_page.assert_called_once_with(1, 10)


def test_get_by_page_rejects_page_below_1(client, mock_service):
    response = client.get("/questions/page?page=0")

    assert response.status_code == 422
    mock_service.get_by_page.assert_not_called()


def test_get_by_page_rejects_page_size_above_50(client, mock_service):
    response = client.get("/questions/page?page_size=51")

    assert response.status_code == 422


def test_page_route_not_swallowed_by_question_id_route(client, mock_service):
    """Regression guard: /questions/page must be registered before
    /questions/{question_id}."""
    mock_service.get_by_page.return_value = {
        "data": [], "page": 1, "page_size": 10, "total": 0, "total_pages": 0
    }

    response = client.get("/questions/page")

    assert response.status_code == 200
    mock_service.get_by_id.assert_not_called()


def test_get_by_id_returns_question(client, mock_service):
    mock_service.get_by_id.return_value = {
        "question_id": 1, "question_label": "Q", "default_answer": "Yes"
    }

    response = client.get("/questions/1")

    assert response.status_code == 200
    mock_service.get_by_id.assert_called_once_with(1)


def test_get_by_id_propagates_404_from_service(client, mock_service):
    mock_service.get_by_id.side_effect = HTTPException(status_code=404, detail="Question not found")

    response = client.get("/questions/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Question not found"}


def test_create_question_returns_201(client, mock_service):
    mock_service.create_question.return_value = {
        "question_id": 2, "question_label": "New?", "default_answer": "No"
    }

    response = client.post("/questions/", json={"question_label": "New?", "default_answer": "No"})

    assert response.status_code == 201


def test_create_question_rejects_missing_required_field(client, mock_service):
    response = client.post("/questions/", json={"default_answer": "No"})

    assert response.status_code == 422
    mock_service.create_question.assert_not_called()


def test_update_question_returns_200(client, mock_service):
    mock_service.update_question.return_value = {
        "question_id": 1, "question_label": "Updated", "default_answer": "Yes"
    }

    response = client.put(
        "/questions/1", json={"question_label": "Updated", "default_answer": "Yes"}
    )

    assert response.status_code == 200


def test_delete_question_returns_204(client, mock_service):
    mock_service.delete_question.return_value = None

    response = client.delete("/questions/1")

    assert response.status_code == 204
    mock_service.delete_question.assert_called_once_with(1)


def test_delete_question_returns_409_via_global_handler_on_integrity_error(client, mock_service):
    mock_service.delete_question.side_effect = IntegrityError("stmt", {}, Exception("fk"))

    response = client.delete("/questions/1")

    assert response.status_code == 409
