from unittest.mock import patch

import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.api.exception_handlers import register_exception_handler
from app.api.routes.products_router import router as products_router


@pytest.fixture
def client():
    app = FastAPI()
    register_exception_handler(app)
    app.include_router(products_router)
    return TestClient(app)


@pytest.fixture
def mock_service():
    with patch("app.api.routes.products_router.ProductService") as mock_cls:
        yield mock_cls.return_value


def test_get_products_returns_list(client, mock_service):
    mock_service.get_products.return_value = [
        {"product_id": 1, "product_label": "Audi", "isActive": True}
    ]

    response = client.get("/products/")

    assert response.status_code == 200
    assert response.json() == [{"product_id": 1, "product_label": "Audi", "isActive": True}]


def test_get_by_id_returns_product(client, mock_service):
    mock_service.get_by_id.return_value = {
        "product_id": 1, "product_label": "Audi", "isActive": True
    }

    response = client.get("/products/1")

    assert response.status_code == 200
    assert response.json()["product_label"] == "Audi"
    mock_service.get_by_id.assert_called_once_with(1)


def test_get_by_id_propagates_404_from_service(client, mock_service):
    mock_service.get_by_id.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
    )

    response = client.get("/products/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_create_product_returns_201(client, mock_service):
    mock_service.create_product.return_value = {
        "product_id": 2, "product_label": "BMW", "isActive": True
    }

    response = client.post("/products/", json={"product_label": "BMW", "isActive": True})

    assert response.status_code == 201
    assert response.json()["product_label"] == "BMW"


def test_create_product_rejects_missing_required_field(client, mock_service):
    """Pydantic request validation runs before the route handler at all —
    this exercises a path the service-layer tests can't reach."""
    response = client.post("/products/", json={"isActive": True})

    assert response.status_code == 422
    mock_service.create_product.assert_not_called()


def test_update_product_returns_200(client, mock_service):
    mock_service.update_product.return_value = {
        "product_id": 1, "product_label": "Audi Updated", "isActive": False
    }

    response = client.put("/products/1", json={"product_label": "Audi Updated", "isActive": False})

    assert response.status_code == 200
    assert response.json()["product_label"] == "Audi Updated"


def test_delete_product_returns_204(client, mock_service):
    mock_service.delete_product.return_value = None

    response = client.delete("/products/1")

    assert response.status_code == 204
    mock_service.delete_product.assert_called_once_with(1)


def test_delete_product_returns_409_via_global_handler_on_integrity_error(client, mock_service):
    """Confirms the router is actually wired to the global IntegrityError
    handler end-to-end, not just that the service lets it propagate
    (already covered separately in test_product_service.py)."""
    mock_service.delete_product.side_effect = IntegrityError("stmt", {}, Exception("fk"))

    response = client.delete("/products/1")

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Cannot delete: this record is still referenced by another record"
    }
