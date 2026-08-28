from fastapi import APIRouter, status, Query

from app.schemas.question_catalog import (
    QuestionCatalogCreate,
    QuestionCatalogResponse,
    QuestionCatalogPage,
)
from app.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("/", response_model=list[QuestionCatalogResponse])
async def get_questions():
    return QuestionService().get_questions()

# Implementing Offset Pagination
@router.get("/page", response_model=QuestionCatalogPage)
async def get_by_page(
    page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=50)
):
    return QuestionService().get_by_page(page, page_size)

@router.get("/{question_id}", response_model=QuestionCatalogResponse)
async def get_by_id(question_id: int):
    return QuestionService().get_by_id(question_id)


@router.post("/", response_model=QuestionCatalogResponse, status_code=status.HTTP_201_CREATED)
async def create_question(question: QuestionCatalogCreate):
    return QuestionService().create_question(question)


@router.put("/{question_id}", response_model=QuestionCatalogResponse)
async def update_question(question_id: int, question: QuestionCatalogCreate):
    return QuestionService().update_question(question_id, question)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(question_id: int):
    QuestionService().delete_question(question_id)
