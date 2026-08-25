from fastapi import APIRouter, status

from app.schemas.question_catalog import QuestionCatalogCreate, QuestionCatalogResponse
from app.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("/", response_model=list[QuestionCatalogResponse])
async def get_answers():
    return QuestionService().get_questions()


@router.get("/{question_id}", response_model=QuestionCatalogResponse)
async def get_by_id(question_id: str):
    return QuestionService().get_by_id(question_id)


@router.post("/", response_model=QuestionCatalogResponse, status_code=status.HTTP_201_CREATED)
async def create_question(question: QuestionCatalogCreate):
    return QuestionService().create_question(question)


@router.put("/{question_id}", response_model=QuestionCatalogResponse)
async def update_question(question_id: str, question: QuestionCatalogCreate):
    return QuestionService().update_question(question_id, question)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(question_id: str):
    QuestionService().delete_question(question_id)
