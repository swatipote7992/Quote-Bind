from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.schemas.product_catalog import ProductCatalogCreate
from app.services.product_service import ProductService


def _service_with_mock_repo() -> ProductService:
    service = ProductService()
    service.product_repository = MagicMock()
    return service


def test_get_by_id_raises_404_when_missing():
    service = _service_with_mock_repo()
    service.product_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_by_id(9999999)

    assert exc.value.status_code == 404


def test_get_by_id_returns_product_when_found():
    service = _service_with_mock_repo()
    product = {"product_id": 1, "product_label": "Audi", "isActive": True}
    service.product_repository.get_by_id.return_value = product
    assert service.get_by_id(1) == product


def test_get_products_returns_all_products():
    service = _service_with_mock_repo()
    products = [{"product_id": 1, "product_label": "Audi", "isActive": True}]
    service.product_repository.get_all.return_value = products

    assert service.get_products() == products


def test_get_by_label_raises_404_when_missing():
    service = _service_with_mock_repo()
    service.product_repository.get_by_label.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_by_label("Nonexistent")

    assert exc.value.status_code == 404


def test_get_by_label_returns_product_when_found():
    service = _service_with_mock_repo()
    product = {"product_id": 1, "product_label": "Audi", "isActive": True}
    service.product_repository.get_by_label.return_value = product

    assert service.get_by_label("Audi") == product


def test_update_product_returns_updated_product():
    service = _service_with_mock_repo()
    updated = {"product_id": 1, "product_label": "Audi Updated", "isActive": False}
    service.product_repository.update.return_value = updated

    result = service.update_product(
        1, ProductCatalogCreate(product_label="Audi Updated", isActive=False)
    )

    assert result == updated


def test_update_product_raises_404_when_missing():
    service = _service_with_mock_repo()
    service.product_repository.update.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.update_product(999, ProductCatalogCreate(product_label="X", isActive=True))

    assert exc.value.status_code == 404


def test_create_product_raises_409_on_duplicate_label():
    service = _service_with_mock_repo()
    product = {"product_id": 1, "product_label": "Audi", "isActive": True}
    service.product_repository.get_by_label.return_value = product

    with pytest.raises(HTTPException) as exc:
        service.create_product(ProductCatalogCreate(product_label="Audi", isActive=True))

    assert exc.value.status_code == 409
    service.product_repository.create.assert_not_called()


def test_create_product_creates_when_label_is_unique():
    service = _service_with_mock_repo()
    service.product_repository.get_by_label.return_value = None
    created = {"product_id": 2, "product_label": "BMW", "isActive": True}
    service.product_repository.create.return_value = created

    result = service.create_product(ProductCatalogCreate(product_label="BMW", isActive=True))

    assert result == created
    service.product_repository.create.assert_called_once_with("BMW", True)


def test_delete_product_raises_404_when_missing():
    service = _service_with_mock_repo()
    service.product_repository.delete.return_value = False

    with pytest.raises(HTTPException) as exc_info:
        service.delete_product(999)

    assert exc_info.value.status_code == 404


def test_delete_product_does_not_catch_integrity_error():
    """IntegrityError is now handled globally (app/api/exception_handlers.py),
    not in the service — this test guards that regression."""
    service = _service_with_mock_repo()
    service.product_repository.delete.side_effect = IntegrityError("stmt", {}, Exception("fk"))

    with pytest.raises(IntegrityError):
        service.delete_product(1)
