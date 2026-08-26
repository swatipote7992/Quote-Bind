from pydantic import BaseModel


class ProductCatalogCreate(BaseModel):
    product_label: str
    isActive: bool = True

class ProductCatalogResponse(BaseModel):
    product_id: int
    product_label: str
    isActive: bool