from sqlalchemy import Boolean, Column, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class ProductCatalog(Base):
    __tablename__ = "product_catalog"

    product_id = Column(String, primary_key=True, index=True)
    product_label = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False)

    question_set = relationship("QuestionSet", back_populates="product", uselist=False)


class QuestionCatalog(Base):
    __tablename__ = "question_catalog"

    question_id = Column(String, primary_key=True, index=True)
    question_label = Column(String, nullable=False)
    default_answer = Column(String, nullable=False)


class QuestionSetArray(Base):
    __tablename__ = "question_array"

    question_set_id = Column(String, ForeignKey("question_set.id"), primary_key=True)
    question_id = Column(
        String, ForeignKey("question_catalog.question_id"), primary_key=True
    )
    answer_value = Column(String, nullable=True)

    question_set = relationship("QuestionSet", back_populates="questions")
    question = relationship("QuestionCatalog")


class QuestionSet(Base):
    __tablename__ = "question_set"

    id = Column(String, primary_key=True, index=True)
    label = Column(String, nullable=False)
    product_id = Column(
        String, ForeignKey("product_catalog.product_id"), nullable=False, unique=True
    )

    product = relationship("ProductCatalog", back_populates="question_set")
    questions = relationship(
        "QuestionSetArray",
        back_populates="question_set",
        cascade="all, delete-orphan",
    )

class Applicant(Base):
    __tablename__ = "applicant"

    id = Column(Integer, primary_key=True, index=True)
    applicant_ref_id = Column(Integer, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    dob = Column(String, nullable=False)

class Quote(Base):
    __tablename__ = "quotes"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=False)
    product_id = Column(String, ForeignKey("product_catalog.product_id"), nullable=False)
    applicant_id = Column(Integer, ForeignKey("applicant.id"), nullable=False)
    premium = Column(JSON, nullable=True)
    policy_id = Column(String, nullable=True)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    applicant = relationship("Applicant", uselist=False)
    product = relationship("ProductCatalog")