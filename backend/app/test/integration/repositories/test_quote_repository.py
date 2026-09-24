from datetime import datetime, timezone

import pytest

from app.models.quote_model import Applicant, QuestionCatalog, QuestionSet, QuoteAnswer
from app.repositories.product_repository import ProductRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.quote_repository import (
    QuoteRepository,
    UnknownProductIdError,
    UnknownQuestionIdError,
)

pytestmark = pytest.mark.usefixtures("db_session")


def _seed_product_with_question_set(db_session, product_label, question_labels):
    """Creates a product + questions via the real repositories (dogfoods the
    code under test), then wires them into a QuestionSet directly via the
    ORM — there's no repository/service for QuestionSet in this app; it's
    only ever managed via the raw seed scripts in app/database/scripts/."""
    product_id = ProductRepository().create(product_label, True)["product_id"]
    question_ids = [
        QuestionRepository().create(label, "Yes")["question_id"] for label in question_labels
    ]

    with db_session() as db:
        questions = (
            db.query(QuestionCatalog).filter(QuestionCatalog.question_id.in_(question_ids)).all()
        )
        qset = QuestionSet(id=f"QS-{product_label}", label=f"{product_label} Set", product_id=product_id)
        qset.questions_set = questions
        db.add(qset)
        db.commit()

    return product_id


def _applicant_payload(ref_id=1001, first_name="Jane"):
    return {
        "applicant_id": ref_id,
        "first_name": first_name,
        "last_name": "Doe",
        "email": "jane@example.com",
        "phone": "1234567890",
        "date_of_birth": "1990-01-01",
    }


def _quote_document(quote_id, product_id, applicant=None, answers=None):
    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": quote_id,
        "status": "New",
        "product_id": product_id,
        "applicant": applicant or _applicant_payload(),
        "answers": answers,
        "created_at": now,
        "updated_at": now,
    }


def _question_ids(db_session):
    """All question_ids in the catalog, in creation order."""
    with db_session() as db:
        return [q.question_id for q in db.query(QuestionCatalog).order_by(QuestionCatalog.question_id)]


def test_save_quote_and_get_by_id(db_session):
    product_id = _seed_product_with_question_set(db_session, "Audi", ["Q1", "Q2"])
    repo = QuoteRepository()

    saved = repo.save_quote(_quote_document("Q001", product_id))

    assert saved["id"] == "Q001"
    assert saved["product_id"] == product_id
    assert saved["applicant"]["first_name"] == "Jane"
    assert {q["question_label"] for q in saved["question_set"]} == {"Q1", "Q2"}
    assert repo.get_by_id("Q001") == saved


def test_save_quote_raises_unknown_product_id_error():
    repo = QuoteRepository()
    with pytest.raises(UnknownProductIdError):
        repo.save_quote(_quote_document("Q001", 999))


def test_get_by_id_returns_none_when_missing():
    repo = QuoteRepository()
    assert repo.get_by_id("QNOPE") is None


def test_get_quotes_returns_all(db_session):
    product_id = _seed_product_with_question_set(db_session, "Audi", ["Q1"])
    repo = QuoteRepository()
    repo.save_quote(_quote_document("Q001", product_id))
    repo.save_quote(_quote_document("Q002", product_id, _applicant_payload(1002, "Bob")))

    assert {q["id"] for q in repo.get_quotes()} == {"Q001", "Q002"}


def test_update_quote_reresolves_question_set_on_product_change(db_session):
    product_a = _seed_product_with_question_set(db_session, "Audi", ["Q1", "Q2"])
    product_b = _seed_product_with_question_set(db_session, "BMW", ["Q3"])
    repo = QuoteRepository()
    repo.save_quote(_quote_document("Q001", product_a))

    updated = repo.update_quote("Q001", {"product_id": product_b})

    assert updated["product_id"] == product_b
    assert {q["question_label"] for q in updated["question_set"]} == {"Q3"}


def test_update_quote_updates_applicant_fields(db_session):
    product_id = _seed_product_with_question_set(db_session, "Audi", ["Q1"])
    repo = QuoteRepository()
    repo.save_quote(_quote_document("Q001", product_id))

    updated = repo.update_quote(
        "Q001", {"applicant": _applicant_payload(1001, "Janet")}
    )

    assert updated["applicant"]["first_name"] == "Janet"


def test_update_quote_raises_unknown_product_id_error(db_session):
    product_id = _seed_product_with_question_set(db_session, "Audi", ["Q1"])
    repo = QuoteRepository()
    repo.save_quote(_quote_document("Q001", product_id))

    with pytest.raises(UnknownProductIdError):
        repo.update_quote("Q001", {"product_id": 999})


def test_update_quote_returns_none_when_missing():
    repo = QuoteRepository()
    assert repo.update_quote("QNOPE", {"product_id": 1}) is None


def test_delete_quote_removes_quote_and_applicant(db_session):
    product_id = _seed_product_with_question_set(db_session, "Audi", ["Q1"])
    repo = QuoteRepository()
    repo.save_quote(_quote_document("Q001", product_id))

    assert repo.delete_quote("Q001") is True
    assert repo.get_by_id("Q001") is None

    with db_session() as db:
        assert db.query(Applicant).filter(Applicant.applicant_ref_id == 1001).first() is None


def test_delete_quote_returns_false_when_missing():
    repo = QuoteRepository()
    assert repo.delete_quote("QNOPE") is False


def test_get_by_cursor_paginates_in_id_order(db_session):
    product_id = _seed_product_with_question_set(db_session, "Audi", ["Q1"])
    repo = QuoteRepository()
    for i in range(1, 6):
        repo.save_quote(
            _quote_document(f"Q{i:03d}", product_id, _applicant_payload(1000 + i, f"Person{i}"))
        )

    page_1, has_more_1 = repo.get_by_cursor(after=None, limit=2)
    page_2, has_more_2 = repo.get_by_cursor(after=page_1[-1]["id"], limit=2)

    assert [q["id"] for q in page_1] == ["Q001", "Q002"]
    assert has_more_1 is True
    assert [q["id"] for q in page_2] == ["Q003", "Q004"]
    assert has_more_2 is True


def test_get_by_cursor_has_more_false_on_last_page(db_session):
    product_id = _seed_product_with_question_set(db_session, "Audi", ["Q1"])
    repo = QuoteRepository()
    repo.save_quote(_quote_document("Q001", product_id))

    page, has_more = repo.get_by_cursor(after=None, limit=10)

    assert [q["id"] for q in page] == ["Q001"]
    assert has_more is False


def test_search_quotes_by_category(db_session):
    audi_id = _seed_product_with_question_set(db_session, "Audi", ["Q1"])
    bmw_id = _seed_product_with_question_set(db_session, "BMW", ["Q1"])
    repo = QuoteRepository()
    repo.save_quote(_quote_document("Q001", audi_id))
    repo.save_quote(_quote_document("Q002", bmw_id, _applicant_payload(1002, "Bob")))

    results = repo.search_quotes(category="Audi")

    assert [q["id"] for q in results] == ["Q001"]


def test_search_quotes_by_name_matches_first_or_last_name_case_insensitively(db_session):
    product_id = _seed_product_with_question_set(db_session, "Audi", ["Q1"])
    repo = QuoteRepository()
    repo.save_quote(_quote_document("Q001", product_id, _applicant_payload(1001, "Jane")))
    repo.save_quote(_quote_document("Q002", product_id, _applicant_payload(1002, "Bob")))

    results = repo.search_quotes(name="jane")

    assert [q["id"] for q in results] == ["Q001"]


def test_save_quote_defaults_every_answer_when_none_supplied(db_session):
    product_id = _seed_product_with_question_set(db_session, "Audi", ["Q1", "Q2"])

    saved = QuoteRepository().save_quote(_quote_document("Q001", product_id))

    assert [(q["default_answer"], q["answer"]) for q in saved["question_set"]] == [
        ("Yes", "Yes"),
        ("Yes", "Yes"),
    ]


def test_save_quote_stores_supplied_answer_alongside_default(db_session):
    product_id = _seed_product_with_question_set(db_session, "Audi", ["Q1", "Q2"])
    first, second = _question_ids(db_session)
    repo = QuoteRepository()

    saved = repo.save_quote(
        _quote_document("Q001", product_id, answers=[{"question_id": second, "answer": "No"}])
    )

    by_id = {q["question_id"]: q for q in saved["question_set"]}
    assert by_id[first]["answer"] == "Yes"  # not supplied -> default
    assert by_id[second]["default_answer"] == "Yes"
    assert by_id[second]["answer"] == "No"
    assert repo.get_by_id("Q001") == saved


def test_save_quote_rejects_answer_for_question_outside_the_product(db_session):
    audi = _seed_product_with_question_set(db_session, "Audi", ["Q1"])
    _seed_product_with_question_set(db_session, "BMW", ["Q2"])
    _, bmw_question = _question_ids(db_session)
    repo = QuoteRepository()

    with pytest.raises(UnknownQuestionIdError):
        repo.save_quote(
            _quote_document("Q001", audi, answers=[{"question_id": bmw_question, "answer": "No"}])
        )

    assert repo.get_by_id("Q001") is None


def test_update_quote_replaces_answers(db_session):
    product_id = _seed_product_with_question_set(db_session, "Audi", ["Q1", "Q2"])
    first, _ = _question_ids(db_session)
    repo = QuoteRepository()
    repo.save_quote(_quote_document("Q001", product_id))

    updated = repo.update_quote("Q001", {"answers": [{"question_id": first, "answer": "No"}]})

    by_id = {q["question_id"]: q["answer"] for q in updated["question_set"]}
    assert by_id[first] == "No"
    assert repo.get_by_id("Q001") == updated


def test_update_quote_without_answers_keeps_existing_answers(db_session):
    product_id = _seed_product_with_question_set(db_session, "Audi", ["Q1"])
    (question_id,) = _question_ids(db_session)
    repo = QuoteRepository()
    repo.save_quote(
        _quote_document("Q001", product_id, answers=[{"question_id": question_id, "answer": "No"}])
    )

    updated = repo.update_quote("Q001", {"applicant": _applicant_payload(1001, "Janet")})

    assert [q["answer"] for q in updated["question_set"]] == ["No"]


def test_update_quote_resets_answers_when_product_changes(db_session):
    product_a = _seed_product_with_question_set(db_session, "Audi", ["Q1"])
    product_b = _seed_product_with_question_set(db_session, "BMW", ["Q2"])
    first, _ = _question_ids(db_session)
    repo = QuoteRepository()
    repo.save_quote(
        _quote_document("Q001", product_a, answers=[{"question_id": first, "answer": "No"}])
    )

    updated = repo.update_quote("Q001", {"product_id": product_b})

    assert [(q["question_label"], q["answer"]) for q in updated["question_set"]] == [("Q2", "Yes")]


def test_quote_without_stored_answers_falls_back_to_defaults(db_session):
    product_id = _seed_product_with_question_set(db_session, "Audi", ["Q1"])
    repo = QuoteRepository()
    repo.save_quote(_quote_document("Q001", product_id))
    with db_session() as db:
        db.query(QuoteAnswer).delete()
        db.commit()

    quote = repo.get_by_id("Q001")

    assert [(q["question_label"], q["default_answer"], q["answer"]) for q in quote["question_set"]] == [
        ("Q1", "Yes", "Yes")
    ]


def test_delete_quote_removes_its_answers(db_session):
    product_id = _seed_product_with_question_set(db_session, "Audi", ["Q1"])
    repo = QuoteRepository()
    repo.save_quote(_quote_document("Q001", product_id))

    assert repo.delete_quote("Q001") is True

    with db_session() as db:
        assert db.query(QuoteAnswer).count() == 0
