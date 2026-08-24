from sqlalchemy import Column, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Applicant(Base):
    __tablename__ = "applicant"

    id = Column(Integer, primary_key=True, index=True)
    applicant_ref_id = Column(Integer, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    dob = Column(String, nullable=False)


class QuestionCatalog(Base):
    __tablename__ = "question_catalog"

    question_id = Column(String, primary_key=True, index=True)
    question_label = Column(String, nullable=False)
    default_answer = Column(String, nullable=False)


class Answer(Base):
    __tablename__ = "answer"

    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(String, ForeignKey("quotes.id"), nullable=False)
    question_id = Column(
        String, ForeignKey("question_catalog.question_id"), nullable=False
    )
    question_label = Column(String, nullable=False)
    answer_value = Column(String, nullable=False)

    quote = relationship("Quote", back_populates="answers")


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=False)
    product_type = Column(String, nullable=False)
    applicant_id = Column(Integer, ForeignKey("applicant.id"), nullable=False)
    premium = Column(JSON, nullable=True)
    policy_id = Column(String, nullable=True)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    applicant = relationship("Applicant", uselist=False)
    answers = relationship(
        "Answer", back_populates="quote", cascade="all, delete-orphan"
    )