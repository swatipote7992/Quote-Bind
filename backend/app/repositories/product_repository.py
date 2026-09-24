from sqlalchemy import select

from app.database.database import SessionLocal

from app.models.quote_model import ProductCatalog, QuestionCatalog, QuestionSet, question_array

class ProductRepository:

    def _to_document(self, entry: ProductCatalog) -> dict:
        return {
            "product_id": entry.product_id,
            "product_label": entry.product_label,
            "isActive": entry.is_active,
        }

    def get_all(self) -> list[dict]:
        with SessionLocal() as db:
            entries = db.execute(select(ProductCatalog)).scalars().all()
            return [self._to_document(entry) for entry in entries]

    def get_by_id(self, product_id: int) -> dict | None:
        with SessionLocal() as db:
            entry = (
                db.execute(select(ProductCatalog).where(ProductCatalog.product_id == product_id))
                .scalars()
                .first()
            )
            return self._to_document(entry) if entry else None

    def get_questions(self, product_id: int) -> list[dict]:
        # product -> question_set (by product_id) -> question_array rows for that
        # set -> the matching question_catalog entries.
        with SessionLocal() as db:
            entries = (
                db.execute(
                    select(QuestionCatalog)
                    .join(
                        question_array,
                        question_array.c.question_id == QuestionCatalog.question_id,
                    )
                    .join(QuestionSet, QuestionSet.id == question_array.c.question_set_id)
                    .where(QuestionSet.product_id == product_id)
                    .order_by(QuestionCatalog.question_id)
                )
                .scalars()
                .all()
            )
            return [
                {
                    "question_id": entry.question_id,
                    "question_label": entry.question_label,
                    "default_answer": entry.default_answer,
                }
                for entry in entries
            ]

    def get_by_label(self, label: str) -> dict | None:
        with SessionLocal() as db:
            entry = (
                db.execute(select(ProductCatalog).where(ProductCatalog.product_label == label))
                .scalars()
                .first()
            )
            return self._to_document(entry) if entry else None

    def create(self, product_label: str, isActive: bool) -> dict:
        with SessionLocal() as db:
            entry = ProductCatalog(
                product_label=product_label,
                is_active=isActive,
            )
            db.add(entry)
            db.commit()
            db.refresh(entry)
            return self._to_document(entry)

    def update(self, product_id: int, updates: dict) -> dict | None:
        with SessionLocal() as db:
            entry = (
                db.execute(select(ProductCatalog).where(ProductCatalog.product_id == product_id))
                .scalars()
                .first()
            )
            if not entry:
                return None

            if updates.get("product_label") is not None:
                entry.product_label = updates["product_label"]

            if updates.get("isActive") is not None:
                entry.is_active = updates["isActive"]

            db.commit()
            db.refresh(entry)
            return self._to_document(entry)

    def delete(self, product_id: int) -> bool:
        with SessionLocal() as db:
            entry = (
                db.execute(select(ProductCatalog).where(ProductCatalog.product_id == product_id))
                .scalars()
                .first()
            )
            if not entry:
                return False

            db.delete(entry)
            db.commit()
            return True
