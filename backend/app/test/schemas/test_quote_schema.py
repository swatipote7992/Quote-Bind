from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.schemas.quote import Applicant, QuestionAnswerInput, QuoteCreate


def _make_applicant(dob: date) -> Applicant:
    return Applicant(
        applicant_id=1,
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        phone="1234567890",
        date_of_birth=dob,
    )


def test_accepts_past_date_of_birth():
    applicant = _make_applicant(date(1990, 1, 1))
    assert applicant.date_of_birth == date(1990, 1, 1)


def test_rejects_future_date_of_birth():
    with pytest.raises(ValidationError):
        _make_applicant(date.today() + timedelta(days=1))


def test_rejects_todays_date_as_date_of_birth():
    with pytest.raises(ValidationError):
        _make_applicant(date.today())


def test_quote_create_answers_are_optional():
    quote = QuoteCreate(product_id=1, applicant=_make_applicant(date(1990, 1, 1)))
    assert quote.answers is None


def test_rejects_empty_answer():
    with pytest.raises(ValidationError):
        QuestionAnswerInput(question_id=1, answer="")
