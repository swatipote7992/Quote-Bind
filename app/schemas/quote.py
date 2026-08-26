from pydantic import BaseModel, EmailStr
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


class QuestionResponse(BaseModel):
    question_id: int
    question_label: str

class Premium(BaseModel):
    amount: float
    currency: str
    calculated_at: datetime

class Status(Enum):
    new = "New"
    inprogress = "InProgress"
    pending = "Pending"
    approved = "Approved"
    rejected = "Rejected"

class QuoteCreate(BaseModel):
    product_id: str
    applicant: Applicant


class QuoteResponse(BaseModel):
    id: str
    status: Status
    product_id: str
    applicant: Applicant
    question_set: list[QuestionResponse]
    premium: Premium | None = None
    policy_id: str | None = None
    created_at: datetime
    updated_at: datetime