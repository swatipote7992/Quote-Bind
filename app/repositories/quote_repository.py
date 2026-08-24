from sqlalchemy.orm import Query, Session, joinedload

from app.database.database import SessionLocal
from app.models.quote_model import Answer, Applicant, Quote


class QuoteRepository:

    def _to_document(self, quote: Quote) -> dict:
        return {
            "id": quote.id,
            "status": quote.status,
            "product_type": quote.product_type,
            "applicant": {
                "applicant_id": quote.applicant.applicant_ref_id,
                "first_name": quote.applicant.first_name,
                "last_name": quote.applicant.last_name,
                "email": quote.applicant.email,
                "phone": quote.applicant.phone,
                "date_of_birth": quote.applicant.dob,
            },
            "answers": [
                {
                    "question_id": answer.question_id,
                    "question_label": answer.question_label,
                    "answer_value": answer.answer_value,
                }
                for answer in quote.answers
            ],
            "premium": quote.premium,
            "policy_id": quote.policy_id,
            "created_at": quote.created_at,
            "updated_at": quote.updated_at,
        }

    def _query(self, db: Session) -> Query:
        return db.query(Quote).options(
            joinedload(Quote.applicant), joinedload(Quote.answers)
        )

    def get_quotes(self) -> list[dict]:
        with SessionLocal() as db:
            quotes = self._query(db).all()
            return [self._to_document(quote) for quote in quotes]

    def get_by_id(self, quote_id: str) -> dict | None:
        with SessionLocal() as db:
            quote = self._query(db).filter(Quote.id == quote_id).first()
            return self._to_document(quote) if quote else None

    def save_quote(self, quote_document: dict) -> dict:
        with SessionLocal() as db:
            applicant_data = quote_document["applicant"]
            applicant = Applicant(
                applicant_ref_id=applicant_data["applicant_id"],
                first_name=applicant_data["first_name"],
                last_name=applicant_data["last_name"],
                email=applicant_data["email"],
                phone=applicant_data["phone"],
                dob=applicant_data["date_of_birth"],
            )
            db.add(applicant)
            db.flush()

            quote = Quote(
                id=quote_document["id"],
                status=quote_document["status"],
                product_type=quote_document["product_type"],
                applicant_id=applicant.id,
                premium=quote_document["premium"],
                policy_id=quote_document["policy_id"],
                created_at=quote_document["created_at"],
                updated_at=quote_document["updated_at"],
                answers=[
                    Answer(
                        question_id=answer["question_id"],
                        question_label=answer["question_label"],
                        answer_value=answer["answer_value"],
                    )
                    for answer in quote_document["answers"]
                ],
            )
            db.add(quote)
            db.commit()

            return self._to_document(
                self._query(db).filter(Quote.id == quote.id).first()
            )

    def update_quote(self, quote_id: str, updates: dict) -> dict | None:
        with SessionLocal() as db:
            quote = self._query(db).filter(Quote.id == quote_id).first()
            if not quote:
                return None

            if "product_type" in updates:
                quote.product_type = updates["product_type"]

            applicant_data = updates.get("applicant")
            if applicant_data:
                quote.applicant.applicant_ref_id = applicant_data["applicant_id"]
                quote.applicant.first_name = applicant_data["first_name"]
                quote.applicant.last_name = applicant_data["last_name"]
                quote.applicant.email = applicant_data["email"]
                quote.applicant.phone = applicant_data["phone"]
                quote.applicant.dob = applicant_data["date_of_birth"]

            answers_data = updates.get("answers")
            if answers_data is not None:
                quote.answers = [
                    Answer(
                        question_id=answer["question_id"],
                        question_label=answer["question_label"],
                        answer_value=answer["answer_value"],
                    )
                    for answer in answers_data
                ]

            db.commit()

            return self._to_document(
                self._query(db).filter(Quote.id == quote_id).first()
            )

    def delete_quote(self, quote_id: str) -> bool:
        with SessionLocal() as db:
            quote = db.query(Quote).filter(Quote.id == quote_id).first()
            if not quote:
                return False

            if quote.applicant:
                db.delete(quote.applicant)
            db.delete(quote)
            db.commit()
            return True

    def search_quotes(
        self, name: str | None = None, category: str | None = None
    ) -> list[dict]:
        with SessionLocal() as db:
            query = self._query(db)
            if category:
                query = query.filter(Quote.product_type.ilike(category))
            quotes = query.all()

            if name:
                needle = name.lower()
                quotes = [
                    quote
                    for quote in quotes
                    if needle in quote.applicant.first_name.lower()
                    or needle in quote.applicant.last_name.lower()
                ]

            return [self._to_document(quote) for quote in quotes]
