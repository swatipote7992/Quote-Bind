from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.schemas.question_catalog import QuestionCatalogCreate
from app.services.question_service import QuestionService


def _service_with_mock_repo() -> QuestionService:
    service = QuestionService()
    service.question_repository = MagicMock()
    return service


def test_get_by_id_raises_404_when_missing():
    service = _service_with_mock_repo()
    service.question_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_by_id(9999999)

    assert exc.value.status_code == 404


def test_get_by_id_returns_question_when_found():
    service = _service_with_mock_repo()
    question = {"question_id": 1, "question_label": "Are you 18?", "default_answer": "Yes"}
    service.question_repository.get_by_id.return_value = question

    assert service.get_by_id(1) == question


def test_get_questions_returns_all_questions():
    service = _service_with_mock_repo()
    questions = [{"question_id": 1, "question_label": "Q", "default_answer": "Yes"}]
    service.question_repository.get_all.return_value = questions

    assert service.get_questions() == questions


def test_get_by_page_computes_offset_and_total_pages():
    service = _service_with_mock_repo()
    items = [{"question_id": i, "question_label": "Q", "default_answer": "Yes"} for i in range(1, 6)]
    service.question_repository.get_by_page.return_value = (items, 55)

    result = service.get_by_page(page=2, page_size=5)

    service.question_repository.get_by_page.assert_called_once_with(5, 5)  # offset = (2-1)*5
    assert result == {
        "data": items,
        "page": 2,
        "page_size": 5,
        "total": 55,
        "total_pages": 11,
    }


def test_create_question_raises_409_on_duplicate_label():
    service = _service_with_mock_repo()
    service.question_repository.get_by_label.return_value = {
        "question_id": 1, "question_label": "Are you 18?", "default_answer": "Yes"
    }

    with pytest.raises(HTTPException) as exc:
        service.create_question(
            QuestionCatalogCreate(question_label="Are you 18?", default_answer="Yes")
        )

    assert exc.value.status_code == 409
    service.question_repository.create.assert_not_called()


def test_create_question_creates_when_label_is_unique():
    service = _service_with_mock_repo()
    service.question_repository.get_by_label.return_value = None
    created = {"question_id": 2, "question_label": "New?", "default_answer": "No"}
    service.question_repository.create.return_value = created

    result = service.create_question(
        QuestionCatalogCreate(question_label="New?", default_answer="No")
    )

    assert result == created
    service.question_repository.create.assert_called_once_with("New?", "No")


def test_update_question_raises_404_when_missing():
    service = _service_with_mock_repo()
    service.question_repository.update.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.update_question(
            999, QuestionCatalogCreate(question_label="X", default_answer="Yes")
        )

    assert exc.value.status_code == 404


def test_update_question_returns_updated_question():
    service = _service_with_mock_repo()
    updated = {"question_id": 1, "question_label": "Updated", "default_answer": "No"}
    service.question_repository.update.return_value = updated

    result = service.update_question(
        1, QuestionCatalogCreate(question_label="Updated", default_answer="No")
    )

    assert result == updated


def test_delete_question_raises_404_when_missing():
    service = _service_with_mock_repo()
    service.question_repository.delete.return_value = False

    with pytest.raises(HTTPException) as exc:
        service.delete_question(999)

    assert exc.value.status_code == 404


def test_delete_question_does_not_catch_integrity_error():
    """IntegrityError is now handled globally (app/api/exception_handlers.py),
    not in the service — this test guards that regression."""
    service = _service_with_mock_repo()
    service.question_repository.delete.side_effect = IntegrityError("stmt", {}, Exception("fk"))

    with pytest.raises(IntegrityError):
        service.delete_question(1)
