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


class Answer(BaseModel):
    question_id: str
    question_label: str
    answer_value: str

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

class ProductType(Enum):
    audi = "Audi"
    bmw = "BMW"
    mercedes = "Mercedes"

class QuoteCreate(BaseModel):
    product_type: ProductType
    applicant: Applicant
    answers: list[Answer]


class QuoteResponse(BaseModel):
    id: str
    status: Status
    product_type: ProductType
    applicant_id: Applicant
    answers: list[Answer]
    premium: Premium | None = None
    policy_id: str | None = None
    created_at: datetime
    updated_at: datetime