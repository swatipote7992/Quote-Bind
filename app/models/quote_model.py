from sqlalchemy import Boolean, Column, ForeignKey, Integer, JSON, String, Table
from sqlalchemy.orm import relationship

from app.database.database import Base


class ProductCatalog(Base):
    __tablename__ = "product_catalog"

    product_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_label = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False)

    question_set = relationship("QuestionSet", back_populates="product", uselist=False)


class QuestionCatalog(Base):
    __tablename__ = "question_catalog"

    question_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question_label = Column(String, nullable=False)
    default_answer = Column(String, nullable=False)


question_array = Table(
    "question_array",
    Base.metadata,
    Column("question_set_id", String, ForeignKey("question_set.id"), primary_key=True),
    Column(
        "question_id",
        Integer,
        ForeignKey("question_catalog.question_id"),
        primary_key=True,
    ),
)


class QuestionSet(Base):
    __tablename__ = "question_set"

    id = Column(String, primary_key=True, index=True)
    label = Column(String, nullable=False)
    product_id = Column(
        Integer, ForeignKey("product_catalog.product_id"), nullable=False, unique=True
    )

    product = relationship("ProductCatalog", back_populates="question_set")
    questions_set = relationship("QuestionCatalog", secondary=question_array)

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
    product_id = Column(Integer, ForeignKey("product_catalog.product_id"), nullable=False)
    applicant_id = Column(Integer, ForeignKey("applicant.id"), nullable=False)
    premium = Column(JSON, nullable=True)
    policy_id = Column(String, nullable=True)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    applicant = relationship("Applicant", uselist=False)
    product = relationship("ProductCatalog")