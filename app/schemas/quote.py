from pydantic import BaseModel, EmailStr, field_validator
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

class QuestionResponse(BaseModel):
    question_id: int
    question_label: str

class Status(Enum):
    new = "New"
    inprogress = "InProgress"
    pending = "Pending"
    approved = "Approved"
    rejected = "Rejected"

class QuoteCreate(BaseModel):
    product_id: int
    applicant: Applicant


class QuoteResponse(BaseModel):
    id: str
    status: Status
    product_id: int
    applicant: Applicant
    question_set: list[QuestionResponse]
    created_at: datetime
    updated_at: datetime