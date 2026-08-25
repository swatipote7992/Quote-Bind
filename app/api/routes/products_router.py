from fastapi import APIRouter, status

from app.schemas.product_catalog import ProductCatalogCreate, ProductCatalogResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=list[ProductCatalogResponse])
async def get_products():
    return ProductService().get_products()


@router.get("/{product_id}", response_model=ProductCatalogResponse)
async def get_by_id(product_id: str):
    return ProductService().get_by_id(product_id)


@router.post("/", response_model=ProductCatalogResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCatalogCreate):
    return ProductService().create_product(product)


@router.put("/{product_id}", response_model=ProductCatalogResponse)
async def update_product(product_id: str, product: ProductCatalogCreate):
    return ProductService().update_product(product_id, product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str):
    ProductService().delete_product(product_id)
