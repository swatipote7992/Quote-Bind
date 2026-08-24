from fastapi import APIRouter, status

from app.schemas.question_catalog import QuestionCatalogCreate, QuestionCatalogResponse
from app.services.question_service import QuestionService

router = APIRouter(prefix="/answers", tags=["Answers"])


@router.get("/", response_model=list[QuestionCatalogResponse])
async def get_answers():
    return QuestionService().get_answers()


@router.get("/{question_id}", response_model=QuestionCatalogResponse)
async def get_by_id(question_id: str):
    return QuestionService().get_by_id(question_id)


@router.post("/", response_model=QuestionCatalogResponse, status_code=status.HTTP_201_CREATED)
async def create_answer(answer: QuestionCatalogCreate):
    return QuestionService().create_answer(answer)


@router.put("/{question_id}", response_model=QuestionCatalogResponse)
async def update_answer(question_id: str, answer: QuestionCatalogCreate):
    return QuestionService().update_answer(question_id, answer)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(question_id: str):
    QuestionService().delete_answer(question_id)
