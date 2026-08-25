from app.database.database import SessionLocal

from app.models.quote_model import ProductCatalog

class ProductRepository:

    def _to_document(self, entry: ProductCatalog) -> dict:
        return {
            "product_id": entry.product_id,
            "product_label": entry.product_label,
            "isActive": entry.is_active,
        }

    def get_all(self) -> list[dict]:
        with SessionLocal() as db:
            entries = db.query(ProductCatalog).all()
            return [self._to_document(entry) for entry in entries]

    def get_by_id(self, product_id: str) -> dict | None:
        with SessionLocal() as db:
            entry = (
                db.query(ProductCatalog)
                .filter(ProductCatalog.product_id == product_id)
                .first()
            )
            return self._to_document(entry) if entry else None

    def get_by_label(self, label: str) -> dict | None:
        with SessionLocal() as db:
            entry = (
                db.query(ProductCatalog)
                .filter(ProductCatalog.product_label == label)
                .first()
            )
            return self._to_document(entry) if entry else None

    def create(self, product_id: str, product_label: str, isActive: bool) -> dict:
        with SessionLocal() as db:
            entry = ProductCatalog(
                product_id=product_id,
                product_label=product_label,
                is_active=isActive,
            )
            db.add(entry)
            db.commit()
            db.refresh(entry)
            return self._to_document(entry)

    def update(self, product_id: str, updates: dict) -> dict | None:
        with SessionLocal() as db:
            entry = (
                        db.query(ProductCatalog)
                        .filter(ProductCatalog.product_id == product_id)
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

    def delete(self, product_id: str) -> bool:
        with SessionLocal() as db:
            entry = db.query(ProductCatalog).filter(ProductCatalog.product_id == product_id).first()
            if not entry:
                return False
            
            db.delete(entry)
            db.commit()
            return True
                