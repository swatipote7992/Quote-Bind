import pytest

from app.repositories.product_repository import ProductRepository

pytestmark = pytest.mark.usefixtures("db_session")


def test_create_and_get_by_id():
    repo = ProductRepository()
    created = repo.create("Audi", True)

    assert created["product_label"] == "Audi"
    assert created["isActive"] is True
    assert repo.get_by_id(created["product_id"]) == created


def test_get_by_id_returns_none_when_missing():
    repo = ProductRepository()
    assert repo.get_by_id(999) is None


def test_get_by_label_returns_none_when_missing():
    repo = ProductRepository()
    assert repo.get_by_label("Nonexistent") is None


def test_get_by_label_returns_matching_product():
    repo = ProductRepository()
    created = repo.create("Audi", True)
    assert repo.get_by_label("Audi") == created


def test_get_all_returns_all_created_products():
    repo = ProductRepository()
    repo.create("Audi", True)
    repo.create("BMW", False)

    labels = {p["product_label"] for p in repo.get_all()}
    assert labels == {"Audi", "BMW"}


def test_update_changes_fields():
    repo = ProductRepository()
    created = repo.create("Audi", True)

    updated = repo.update(created["product_id"], {"product_label": "Audi Updated", "isActive": False})

    assert updated["product_label"] == "Audi Updated"
    assert updated["isActive"] is False


def test_update_ignores_unset_fields():
    repo = ProductRepository()
    created = repo.create("Audi", True)

    updated = repo.update(created["product_id"], {"product_label": None, "isActive": None})

    assert updated["product_label"] == "Audi"
    assert updated["isActive"] is True


def test_update_returns_none_when_missing():
    repo = ProductRepository()
    assert repo.update(999, {"product_label": "X"}) is None


def test_delete_returns_true_and_removes_row():
    repo = ProductRepository()
    created = repo.create("Audi", True)

    assert repo.delete(created["product_id"]) is True
    assert repo.get_by_id(created["product_id"]) is None


def test_delete_returns_false_when_missing():
    repo = ProductRepository()
    assert repo.delete(999) is False
