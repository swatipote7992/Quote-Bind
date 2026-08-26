from pydantic import BaseModel


class QuestionCatalogCreate(BaseModel):
    question_label: str
    default_answer: str


class QuestionCatalogResponse(BaseModel):
    question_id: int
    question_label: str
    default_answer: str
