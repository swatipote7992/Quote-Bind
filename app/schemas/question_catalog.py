from pydantic import BaseModel


class QuestionCatalogCreate(BaseModel):
    question_label: str
    default_answer: str


class QuestionCatalogResponse(BaseModel):
    question_id: str
    question_label: str
    default_answer: str
