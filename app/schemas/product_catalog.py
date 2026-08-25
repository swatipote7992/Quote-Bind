from pydantic import BaseModel


class ProductCatalogCreate(BaseModel):
    product_label: str
    isActive: bool = True

class ProductCatalogResponse(BaseModel):
    product_id: str
    product_label: str
    isActive: bool