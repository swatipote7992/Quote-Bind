from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.repositories.question_repository import QuestionRepository
from app.schemas.question_catalog import QuestionCatalogCreate


class QuestionService:
    def __init__(self):
        self.question_repository = QuestionRepository()

    def get_answers(self):
        return self.question_repository.get_all()

    def get_by_id(self, question_id: str):
        answer = self.question_repository.get_by_id(question_id)
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found"
            )
        return answer

    def create_answer(self, answer: QuestionCatalogCreate):
        existing_answers = self.question_repository.get_all()
        question_id = f"AC{len(existing_answers) + 1:03d}"
        return self.question_repository.create(
            question_id, answer.question_label, answer.default_answer
        )

    def update_answer(self, question_id: str, answer: QuestionCatalogCreate):
        updated_answer = self.question_repository.update(
            question_id, answer.model_dump()
        )
        if not updated_answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found"
            )
        return updated_answer

    def delete_answer(self, question_id: str) -> None:
        try:
            deleted = self.question_repository.delete(question_id)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete: this question_id is still used by an existing quote",
            ) from exc

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found"
            )
