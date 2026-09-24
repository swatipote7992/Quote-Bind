import pytest

from app.models.quote_model import QuestionCatalog, QuestionSet, question_array
from app.repositories.product_repository import ProductRepository

pytestmark = pytest.mark.usefixtures("db_session")


def test_create_and_get_by_id():
    repo = ProductRepository()
    created = repo.create("Audi", True)

    assert created["product_label"] == "Audi"
    assert created["isActive"] is True
    assert repo.get_by_id(created["product_id"]) == created


def test_get_by_id_returns_none_when_missing():
    repo = ProductRepository()
    assert repo.get_by_id(999) is None


def test_get_by_label_returns_none_when_missing():
    repo = ProductRepository()
    assert repo.get_by_label("Nonexistent") is None


def test_get_by_label_returns_matching_product():
    repo = ProductRepository()
    created = repo.create("Audi", True)
    assert repo.get_by_label("Audi") == created


def test_get_all_returns_all_created_products():
    repo = ProductRepository()
    repo.create("Audi", True)
    repo.create("BMW", False)

    labels = {p["product_label"] for p in repo.get_all()}
    assert labels == {"Audi", "BMW"}


def test_update_changes_fields():
    repo = ProductRepository()
    created = repo.create("Audi", True)

    updated = repo.update(created["product_id"], {"product_label": "Audi Updated", "isActive": False})

    assert updated["product_label"] == "Audi Updated"
    assert updated["isActive"] is False


def test_update_ignores_unset_fields():
    repo = ProductRepository()
    created = repo.create("Audi", True)

    updated = repo.update(created["product_id"], {"product_label": None, "isActive": None})

    assert updated["product_label"] == "Audi"
    assert updated["isActive"] is True


def test_update_returns_none_when_missing():
    repo = ProductRepository()
    assert repo.update(999, {"product_label": "X"}) is None


def test_delete_returns_true_and_removes_row():
    repo = ProductRepository()
    created = repo.create("Audi", True)

    assert repo.delete(created["product_id"]) is True
    assert repo.get_by_id(created["product_id"]) is None


def test_delete_returns_false_when_missing():
    repo = ProductRepository()
    assert repo.delete(999) is False


def test_get_questions_returns_only_the_products_question_set_questions(db_session):
    repo = ProductRepository()
    audi = repo.create("Audi", True)
    bmw = repo.create("BMW", True)

    with db_session() as db:
        db.add_all(
            [
                QuestionCatalog(question_id=1, question_label="Q1", default_answer="Yes"),
                QuestionCatalog(question_id=2, question_label="Q2", default_answer="No"),
                QuestionCatalog(question_id=3, question_label="Q3", default_answer="Yes"),
                QuestionSet(id="QSAU", label="Audi", product_id=audi["product_id"]),
                QuestionSet(id="QSBM", label="BMW", product_id=bmw["product_id"]),
            ]
        )
        db.flush()
        db.execute(
            question_array.insert(),
            [
                {"question_set_id": "QSAU", "question_id": 3},
                {"question_set_id": "QSAU", "question_id": 1},
                {"question_set_id": "QSBM", "question_id": 2},
            ],
        )
        db.commit()

    assert repo.get_questions(audi["product_id"]) == [
        {"question_id": 1, "question_label": "Q1", "default_answer": "Yes"},
        {"question_id": 3, "question_label": "Q3", "default_answer": "Yes"},
    ]


def test_get_questions_returns_empty_list_when_product_has_no_question_set():
    repo = ProductRepository()
    created = repo.create("Audi", True)

    assert repo.get_questions(created["product_id"]) == []
