from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.repositories.question_repository import QuestionRepository
from app.schemas.question_catalog import QuestionCatalogCreate


class QuestionService:
    def __init__(self):
        self.question_repository = QuestionRepository()

    def get_questions(self):
        return self.question_repository.get_all()

    def get_by_page(self, page: int, page_size: int):
        offset = (page - 1) * page_size
        items, total = self.question_repository.get_by_page(offset, page_size)
        total_page = (total + page_size - 1) // page_size

        return {
            "data": items,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_page,
        }

    def get_by_id(self, question_id: int):
        question = self.question_repository.get_by_id(question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
            )
        return question

    def get_by_label(self, label: str):
        question = self.question_repository.get_by_label(label)
        return question

    def create_question(self, question: QuestionCatalogCreate):
        duplicate_question = self.get_by_label(question.question_label)
        if not duplicate_question:
            return self.question_repository.create(
                question.question_label, question.default_answer
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This question already exists",
            )

    def update_question(self, question_id: int, questions: QuestionCatalogCreate):
        updated_questions = self.question_repository.update(
            question_id, questions.model_dump()
        )
        if not updated_questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
            )
        return updated_questions

    def delete_question(self, question_id: int) -> None:
        try:
            deleted = self.question_repository.delete(question_id)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete: this question_id is still used by an existing quote",
            ) from exc

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
            )
