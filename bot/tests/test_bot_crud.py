"""Smoke tests for bot_crud functions using an in-memory SQLite database."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.src.database import Base
from backend.src import models, bot_crud


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def make_dress(db, model="1234", size="38", cup=models.CupSize.B,
               loc=models.StorageLocation.TEL_AVIV,
               cond=models.DressCondition.GOOD,
               status=models.DressStatus.IN_STOCK):
    d = models.DressInventory(
        model_number=model, size=size, cup_size=cup,
        storage_location=loc, dress_condition=cond, status=status,
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def test_get_live_stock_returns_in_stock(db):
    make_dress(db, status=models.DressStatus.IN_STOCK)
    make_dress(db, model="5678", status=models.DressStatus.IN_SEWING)
    result = bot_crud.get_live_stock(db)
    assert len(result) == 1
    assert result[0].model_number == "1234"


def test_get_future_stock_separates_dresses_and_orders(db):
    make_dress(db, status=models.DressStatus.IN_SEWING)
    result = bot_crud.get_future_stock(db)
    assert len(result["dresses"]) == 1
    assert len(result["new_orders"]) == 0


def test_get_dresses_by_model(db):
    make_dress(db, model="ABCD")
    make_dress(db, model="ZZZZ")
    result = bot_crud.get_dresses_by_model(db, "ABCD")
    assert len(result) == 1
    assert result[0].model_number == "ABCD"


def test_get_orders_filtered_no_filter(db):
    result = bot_crud.get_orders_filtered(db)
    assert isinstance(result, list)


def test_update_dress_status_valid(db):
    dress = make_dress(db, status=models.DressStatus.IN_STOCK)
    updated = bot_crud.update_dress_status(db, dress.item_id, "In Sewing")
    assert updated.status == models.DressStatus.IN_SEWING


def test_update_dress_status_not_found(db):
    result = bot_crud.update_dress_status(db, 9999, "In Stock")
    assert result is None


def test_add_dress_creates_record(db):
    dress = bot_crud.add_dress(db, "9999", "40", "C", "Tel Aviv")
    assert dress.item_id is not None
    assert dress.status == models.DressStatus.IN_STOCK
