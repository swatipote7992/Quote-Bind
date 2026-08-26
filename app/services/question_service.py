from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.repositories.question_repository import QuestionRepository
from app.schemas.question_catalog import QuestionCatalogCreate


class QuestionService:
    def __init__(self):
        self.question_repository = QuestionRepository()

    def get_questions(self):
        return self.question_repository.get_all()

    def get_by_id(self, question_id: str):
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
        existing_questions = self.get_questions()
        duplicate_question = self.get_by_label(question.question_label)
        if not duplicate_question:
            question_id = f"AC{len(existing_questions) + 1:03d}"
            return self.question_repository.create(
                question_id, question.question_label, question.default_answer
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This question already exists",
            )

    def update_question(self, question_id: str, questions: QuestionCatalogCreate):
        updated_questions = self.question_repository.update(
            question_id, questions.model_dump()
        )
        if not updated_questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
            )
        return updated_questions

    def delete_question(self, question_id: str) -> None:
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
