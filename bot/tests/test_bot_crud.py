"""Smoke tests for db.repositories functions using an in-memory SQLite database."""

import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from db import engine, Base, get_session, repositories
from db.models import CupSize, DressCondition, DressInventory, DressStatus, OrderType, StorageLocation


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def make_dress(model="1234", size="38", cup=CupSize.B,
               loc=StorageLocation.TEL_AVIV, cond=DressCondition.GOOD,
               status=DressStatus.IN_STOCK):
    with get_session() as db:
        d = DressInventory(
            model_number=model, size=size, cup_size=cup,
            storage_location=loc, dress_condition=cond, status=status,
        )
        db.add(d)
        db.flush()
        item_id = d.item_id
    return item_id


def test_get_live_stock_returns_in_stock():
    make_dress(status=DressStatus.IN_STOCK)
    make_dress(model="5678", status=DressStatus.IN_SEWING)
    with get_session() as db:
        result = repositories.get_live_stock(db)
        assert len(result) == 1
        assert result[0].model_number == "1234"


def test_get_future_stock_separates_dresses_and_orders():
    make_dress(status=DressStatus.IN_SEWING)
    with get_session() as db:
        result = repositories.get_future_stock(db)
        assert len(result["dresses"]) == 1
        assert len(result["new_orders"]) == 0


def test_get_dresses_by_model():
    make_dress(model="ABCD")
    make_dress(model="ZZZZ")
    with get_session() as db:
        result = repositories.get_dresses_by_model(db, "ABCD")
        assert len(result) == 1
        assert result[0].model_number == "ABCD"


def test_get_orders_filtered_no_filter():
    with get_session() as db:
        result = repositories.get_orders_filtered(db)
        assert isinstance(result, list)


def test_update_dress_status_valid():
    item_id = make_dress(status=DressStatus.IN_STOCK)
    with get_session() as db:
        updated = repositories.update_dress_status(db, item_id, "In Sewing")
        assert updated.status == DressStatus.IN_SEWING


def test_update_dress_status_not_found():
    with get_session() as db:
        result = repositories.update_dress_status(db, 9999, "In Stock")
        assert result is None


def test_add_dress_creates_record():
    with get_session() as db:
        dress = repositories.add_dress(db, "9999", "40", "C", "Tel Aviv")
        assert dress.item_id is not None
        assert dress.status == DressStatus.IN_STOCK
