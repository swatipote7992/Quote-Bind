from sqlalchemy.orm import Query, Session, joinedload

from app.database.database import SessionLocal
from app.models.quote_model import Applicant, ProductCatalog, Quote, QuestionSet


class UnknownProductIdError(Exception):
    def __init__(self, product_id: str):
        self.product_id = product_id
        super().__init__(f"Unknown product_id: {product_id}")


class QuoteRepository:

    def _to_document(self, quote: Quote) -> dict:
        return {
            "id": quote.id,
            "status": quote.status,
            "product_id": quote.product_id,
            "applicant": {
                "applicant_id": quote.applicant.applicant_ref_id,
                "first_name": quote.applicant.first_name,
                "last_name": quote.applicant.last_name,
                "email": quote.applicant.email,
                "phone": quote.applicant.phone,
                "date_of_birth": quote.applicant.dob,
            },
            "question_set": [
                {
                    "question_id": question.question_id,
                    "question_label": question.question_label,
                }
                for question in quote.product.question_set.questions_set
            ],
            "premium": quote.premium,
            "policy_id": quote.policy_id,
            "created_at": quote.created_at,
            "updated_at": quote.updated_at,
        }

    def _query(self, db: Session) -> Query:
        return db.query(Quote).options(
            joinedload(Quote.applicant),
            joinedload(Quote.product)
            .joinedload(ProductCatalog.question_set)
            .joinedload(QuestionSet.questions_set),
        )

    def _ensure_product_exists(self, db: Session, product_id: str) -> None:
        exists = (
            db.query(ProductCatalog)
            .filter(ProductCatalog.product_id == product_id)
            .first()
        )
        if not exists:
            raise UnknownProductIdError(product_id)

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
            try:
                self._ensure_product_exists(db, quote_document["product_id"])

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
                    product_id=quote_document["product_id"],
                    applicant_id=applicant.id,
                    premium=quote_document["premium"],
                    policy_id=quote_document["policy_id"],
                    created_at=quote_document["created_at"],
                    updated_at=quote_document["updated_at"],
                )
                db.add(quote)
                db.commit()
            except UnknownProductIdError:
                db.rollback()
                raise

            return self._to_document(
                self._query(db).filter(Quote.id == quote.id).first()
            )

    def update_quote(self, quote_id: str, updates: dict) -> dict | None:
        with SessionLocal() as db:
            quote = self._query(db).filter(Quote.id == quote_id).first()
            if not quote:
                return None

            try:
                if "product_id" in updates:
                    self._ensure_product_exists(db, updates["product_id"])
                    quote.product_id = updates["product_id"]

                applicant_data = updates.get("applicant")
                if applicant_data:
                    quote.applicant.applicant_ref_id = applicant_data["applicant_id"]
                    quote.applicant.first_name = applicant_data["first_name"]
                    quote.applicant.last_name = applicant_data["last_name"]
                    quote.applicant.email = applicant_data["email"]
                    quote.applicant.phone = applicant_data["phone"]
                    quote.applicant.dob = applicant_data["date_of_birth"]

                db.commit()
            except UnknownProductIdError:
                db.rollback()
                raise

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
                query = query.join(Quote.product).filter(
                    ProductCatalog.product_label.ilike(category)
                )
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
