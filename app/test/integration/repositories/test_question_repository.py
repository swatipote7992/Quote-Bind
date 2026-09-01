import pytest

from app.repositories.question_repository import QuestionRepository

pytestmark = pytest.mark.usefixtures("db_session")


def test_create_and_get_by_id():
    repo = QuestionRepository()
    created = repo.create("Are you 18?", "Yes")

    assert created["question_label"] == "Are you 18?"
    assert repo.get_by_id(created["question_id"]) == created


def test_get_by_id_returns_none_when_missing():
    repo = QuestionRepository()
    assert repo.get_by_id(999) is None


def test_get_by_label_returns_none_when_missing():
    repo = QuestionRepository()
    assert repo.get_by_label("Nonexistent") is None


def test_get_all_returns_all_created_questions():
    repo = QuestionRepository()
    repo.create("Q1", "Yes")
    repo.create("Q2", "No")

    assert len(repo.get_all()) == 2


def test_get_by_page_paginates_in_id_order_and_reports_total():
    repo = QuestionRepository()
    for i in range(5):
        repo.create(f"Q{i}", "Yes")

    page_1, total_1 = repo.get_by_page(offset=0, limit=2)
    page_2, total_2 = repo.get_by_page(offset=2, limit=2)

    assert total_1 == 5
    assert total_2 == 5
    assert [q["question_label"] for q in page_1] == ["Q0", "Q1"]
    assert [q["question_label"] for q in page_2] == ["Q2", "Q3"]


def test_get_by_page_returns_empty_past_the_end():
    repo = QuestionRepository()
    repo.create("Q0", "Yes")

    page, total = repo.get_by_page(offset=100, limit=10)

    assert page == []
    assert total == 1


def test_update_changes_fields():
    repo = QuestionRepository()
    created = repo.create("Q1", "Yes")

    updated = repo.update(
        created["question_id"], {"question_label": "Q1 updated", "default_answer": "No"}
    )

    assert updated["question_label"] == "Q1 updated"
    assert updated["default_answer"] == "No"


def test_update_returns_none_when_missing():
    repo = QuestionRepository()
    assert repo.update(999, {"question_label": "X"}) is None


def test_delete_returns_true_and_removes_row():
    repo = QuestionRepository()
    created = repo.create("Q1", "Yes")

    assert repo.delete(created["question_id"]) is True
    assert repo.get_by_id(created["question_id"]) is None


def test_delete_returns_false_when_missing():
    repo = QuestionRepository()
    assert repo.delete(999) is False
