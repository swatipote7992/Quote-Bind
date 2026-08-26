from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.schemas.product_catalog import ProductCatalogCreate
from app.repositories.product_repository import ProductRepository

class ProductService:
    def __init__(self) -> None:
        self.product_repository = ProductRepository()

    def get_products(self):
        return self.product_repository.get_all()

    def get_by_id(self, product_id: int):
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND, detail = "Product not found"
            )
        return product

    def get_by_label(self, label:str):
        product = self.product_repository.get_by_label(label)
        if not product:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        return product

    def create_product(self, product: ProductCatalogCreate):
        duplicate_product = self.product_repository.get_by_label(product.product_label)
        if not duplicate_product:
            new_product = self.product_repository.create(
                product.product_label, product.isActive)
            return new_product
        else:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = "This Product already exist"
            )

    def update_product(self, product_id: int, product: ProductCatalogCreate):
        updated_product = self.product_repository.update(
            product_id, product.model_dump()
        )
        if not updated_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        return updated_product

    def delete_product(self, product_id: int) -> None:
        try:
            deleted = self.product_repository.delete(product_id)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete: this product_id is still in use",
            ) from exc

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )