from app.database.database import SessionLocal
from app.models.quote_model import QuestionCatalog


class QuestionRepository:

    def _to_document(self, entry: QuestionCatalog) -> dict:
        return {
            "question_id": entry.question_id,
            "question_label": entry.question_label,
            "default_answer": entry.default_answer,
        }

    def get_all(self) -> list[dict]:
        with SessionLocal() as db:
            entries = db.query(QuestionCatalog).all()
            return [self._to_document(entry) for entry in entries]

    def get_by_page(self, offset: int, limit: int):
        with SessionLocal() as db:
            entries = (
                db.query(QuestionCatalog)
                .order_by(QuestionCatalog.question_id)
                .offset(offset)
                .limit(limit)
            )
            return [self._to_document(entry) for entry in entries]

    def get_by_id(self, question_id: int) -> dict | None:
        with SessionLocal() as db:
            entry = (
                db.query(QuestionCatalog)
                .filter(QuestionCatalog.question_id == question_id)
                .first()
            )
            return self._to_document(entry) if entry else None

    def get_by_label(self, label: str) -> dict | None:
        with SessionLocal() as db:
            entry = (
                db.query(QuestionCatalog)
                .filter(QuestionCatalog.question_label == label)
                .first()
            )
        return self._to_document(entry) if entry else None

    def create(self, question_label: str, default_answer: str) -> dict:
        with SessionLocal() as db:
            entry = QuestionCatalog(
                question_label=question_label,
                default_answer=default_answer,
            )
            db.add(entry)
            # db.flush()  # We can use Flush to get the generated question_id
            db.commit()
            db.refresh(entry)
            return self._to_document(entry)

    def update(self, question_id: int, updates: dict) -> dict | None:
        with SessionLocal() as db:
            entry = (
                db.query(QuestionCatalog)
                .filter(QuestionCatalog.question_id == question_id)
                .first()
            )
            if not entry:
                return None

            if updates.get("question_label") is not None:
                entry.question_label = updates["question_label"]
            if updates.get("default_answer") is not None:
                entry.default_answer = updates["default_answer"]

            db.commit()
            db.refresh(entry)
            return self._to_document(entry)

    def delete(self, question_id: int) -> bool:
        with SessionLocal() as db:
            entry = (
                db.query(QuestionCatalog)
                .filter(QuestionCatalog.question_id == question_id)
                .first()
            )
            if not entry:
                return False

            db.delete(entry)
            db.commit()
            return True
