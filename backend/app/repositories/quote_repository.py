from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database.database import SessionLocal
from app.models.quote_model import (
    Applicant,
    ProductCatalog,
    Quote,
    QuoteAnswer,
    QuestionSet,
)


class UnknownProductIdError(Exception):
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"Unknown product_id: {product_id}")


class UnknownQuestionIdError(Exception):
    def __init__(self, question_id: int):
        self.question_id = question_id
        super().__init__(f"Question {question_id} is not part of this product's questions")


class QuoteRepository:

    def _question_documents(self, quote: Quote) -> list[dict]:
        if quote.answers:
            return [
                {
                    "question_id": answer.question_id,
                    "question_label": answer.question.question_label,
                    "default_answer": answer.default_answer,
                    "answer": answer.answer,
                }
                for answer in quote.answers
            ]

        # Quotes saved before answers were stored: show the product's questions
        # answered with their defaults.
        questions = quote.product.question_set.questions_set if quote.product.question_set else []
        return [
            {
                "question_id": question.question_id,
                "question_label": question.question_label,
                "default_answer": question.default_answer,
                "answer": question.default_answer,
            }
            for question in sorted(questions, key=lambda q: q.question_id)
        ]

    def _build_answers(
        self, db: Session, product_id: int, provided: list[dict] | None
    ) -> list[QuoteAnswer]:
        """One answer row per question in the product's question set: the
        provided answer if there is one, otherwise the catalog default."""
        question_set = (
            db.execute(select(QuestionSet).where(QuestionSet.product_id == product_id))
            .scalars()
            .first()
        )
        questions = sorted(
            question_set.questions_set if question_set else [],
            key=lambda q: q.question_id,
        )

        given = {item["question_id"]: item["answer"] for item in provided or []}
        unknown = set(given) - {question.question_id for question in questions}
        if unknown:
            raise UnknownQuestionIdError(min(unknown))

        return [
            QuoteAnswer(
                question_id=question.question_id,
                default_answer=question.default_answer,
                answer=given.get(question.question_id, question.default_answer),
            )
            for question in questions
        ]

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
            "question_set": self._question_documents(quote),
            "created_at": quote.created_at,
            "updated_at": quote.updated_at,
        }

    def _query(self) -> Select:
        return select(Quote).options(
            joinedload(Quote.applicant),
            joinedload(Quote.product)
            .joinedload(ProductCatalog.question_set)
            .joinedload(QuestionSet.questions_set),
            selectinload(Quote.answers).joinedload(QuoteAnswer.question),
        )

    def _ensure_product_exists(self, db: Session, product_id: int) -> None:
        exists = (
            db.execute(
                select(ProductCatalog).where(ProductCatalog.product_id == product_id)
            )
            .scalars()
            .first()
        )
        if not exists:
            raise UnknownProductIdError(product_id)

    def get_quotes(self) -> list[dict]:
        with SessionLocal() as db:
            quotes = db.execute(self._query()).unique().scalars().all()
            return [self._to_document(quote) for quote in quotes]

    def get_by_cursor(self, after: str | None, limit: int) -> tuple[list[dict], bool]:
        with SessionLocal() as db:
            stmt = self._query().order_by(Quote.id.asc())
            if after is not None:
                stmt = stmt.where(Quote.id > after)
            stmt = stmt.limit(limit + 1)

            quotes = db.execute(stmt).unique().scalars().all()

            has_more = len(quotes) > limit
            quotes = quotes[:limit]

            return [self._to_document(quote) for quote in quotes], has_more

    def get_by_id(self, quote_id: str) -> dict | None:
        with SessionLocal() as db:
            stmt = self._query().where(Quote.id == quote_id)
            quote = db.execute(stmt).unique().scalars().first()
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
                    created_at=quote_document["created_at"],
                    updated_at=quote_document["updated_at"],
                )
                quote.answers = self._build_answers(
                    db, quote_document["product_id"], quote_document.get("answers")
                )
                db.add(quote)
                db.commit()
            except (UnknownProductIdError, UnknownQuestionIdError):
                db.rollback()
                raise

            stmt = self._query().where(Quote.id == quote.id)
            return self._to_document(db.execute(stmt).unique().scalars().first())

    def update_quote(self, quote_id: str, updates: dict) -> dict | None:
        with SessionLocal() as db:
            stmt = self._query().where(Quote.id == quote_id)
            quote = db.execute(stmt).unique().scalars().first()
            if not quote:
                return None

            try:
                product_changed = False
                if "product_id" in updates:
                    self._ensure_product_exists(db, updates["product_id"])
                    product_changed = quote.product_id != updates["product_id"]
                    quote.product_id = updates["product_id"]

                # Rebuild the answers when they're supplied, or when a new
                # product brings a different set of questions.
                if updates.get("answers") is not None or product_changed:
                    quote.answers = self._build_answers(
                        db, quote.product_id, updates.get("answers")
                    )

                applicant_data = updates.get("applicant")
                if applicant_data:
                    quote.applicant.applicant_ref_id = applicant_data["applicant_id"]
                    quote.applicant.first_name = applicant_data["first_name"]
                    quote.applicant.last_name = applicant_data["last_name"]
                    quote.applicant.email = applicant_data["email"]
                    quote.applicant.phone = applicant_data["phone"]
                    quote.applicant.dob = applicant_data["date_of_birth"]

                db.commit()
            except (UnknownProductIdError, UnknownQuestionIdError):
                db.rollback()
                raise

            stmt = self._query().where(Quote.id == quote_id)
            return self._to_document(db.execute(stmt).unique().scalars().first())

    def delete_quote(self, quote_id: str) -> bool:
        with SessionLocal() as db:
            quote = (
                db.execute(select(Quote).where(Quote.id == quote_id))
                .scalars()
                .first()
            )
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
            stmt = self._query()
            if category:
                stmt = stmt.join(Quote.product).where(
                    ProductCatalog.product_label.ilike(category)
                )
            quotes = db.execute(stmt).unique().scalars().all()

            if name:
                needle = name.lower()
                quotes = [
                    quote
                    for quote in quotes
                    if needle in quote.applicant.first_name.lower()
                    or needle in quote.applicant.last_name.lower()
                ]

            return [self._to_document(quote) for quote in quotes]
