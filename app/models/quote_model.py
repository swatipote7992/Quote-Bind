from 'app.repositories.database' import Base
from sqlalchemy import Column, Integer, String, ForeignKey, JSON

class Applicant(Base):
    __tablename__ = 'applicant'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable = False)
    last_name = Column(String, nullable = False)
    email = Column(String, nullable = False)
    phone = Column(String, nullable = False)
    dob = Column(String, nullable = False)

class Answer(Base):
    __tablename__='answer'

    id = Column(Integer, primary_key=True, index=True)
    question_label = Column(String, nullable=False)
    answer_value = Column(String, nullable=False)

class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index= True)
    status = Column(String, nullable=False)
    product_type = Column(String, nullable=False)
    applicant_id = Column(Integer, ForeignKey("applicant.id"), nullable=False)
    answer_id = Column(Integer, ForeignKey("answer.id"), nullable=False)
    premium = Column(JSON, nullable=True)
    policy_id = Column(String, nullable=True)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)