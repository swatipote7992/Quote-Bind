from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date,datetime
from enum import Enum

# pip install email-validator for EmailStr to work
class Applicant(BaseModel):
    applicant_id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    date_of_birth: date

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: date) -> date:
        if value >= date.today():
            raise ValueError("Date of birth cannot be in the future.")
        return value

class QuestionAnswerInput(BaseModel):
    question_id: int
    answer: str = Field(min_length=1)

class QuestionResponse(BaseModel):
    question_id: int
    question_label: str
    default_answer: str
    answer: str

class Status(Enum):
    new = "New"
    inprogress = "InProgress"
    pending = "Pending"
    approved = "Approved"
    rejected = "Rejected"

class QuoteCreate(BaseModel):
    product_id: int
    applicant: Applicant
    # Answers for the product's questions. Questions left out (or the whole list
    # omitted) fall back to the catalog default answer.
    answers: list[QuestionAnswerInput] | None = None


class QuoteResponse(BaseModel):
    id: str
    status: Status
    product_id: int
    applicant: Applicant
    question_set: list[QuestionResponse]
    created_at: datetime
    updated_at: datetime


class QuoteCursorPage(BaseModel):
    data: list[QuoteResponse]
    next_cursor: str | None
    has_more: bool