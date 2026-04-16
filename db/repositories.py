"""All database query functions for the bridal inventory system."""

from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from .models import (
    ActiveOrder,
    CupSize,
    DressCondition,
    DressInventory,
    DressStatus,
    OrderType,
    StorageLocation,
)


# ---------------------------------------------------------------------------
# Dress queries
# ---------------------------------------------------------------------------

def get_all_dresses(db: Session, skip: int = 0, limit: int = 100) -> List[DressInventory]:
    return db.query(DressInventory).offset(skip).limit(limit).all()


def create_dress(db: Session, dress) -> DressInventory:
    db_dress = DressInventory(**dress.model_dump())
    db.add(db_dress)
    db.flush()
    db.refresh(db_dress)
    return db_dress


def get_live_stock(db: Session) -> List[DressInventory]:
    return (
        db.query(DressInventory)
        .filter(DressInventory.status.in_([DressStatus.IN_STOCK, DressStatus.DISPLAY]))
        .order_by(DressInventory.model_number, DressInventory.size)
        .all()
    )


def get_future_stock(db: Session) -> dict:
    future_statuses = [DressStatus.IN_SEWING, DressStatus.ABROAD, DressStatus.OUT_TO_BRIDE]
    dresses = (
        db.query(DressInventory)
        .filter(DressInventory.status.in_(future_statuses))
        .order_by(DressInventory.status, DressInventory.model_number)
        .all()
    )
    new_orders = (
        db.query(ActiveOrder)
        .filter(ActiveOrder.order_type == OrderType.NEW_ORDER)
        .order_by(ActiveOrder.wedding_date)
        .all()
    )
    return {"dresses": dresses, "new_orders": new_orders}


def get_dresses_by_model(db: Session, model_number: str) -> List[DressInventory]:
    return (
        db.query(DressInventory)
        .filter(DressInventory.model_number.ilike(model_number))
        .order_by(DressInventory.size, DressInventory.cup_size)
        .all()
    )


def update_dress_status(
    db: Session, item_id: int, new_status: str
) -> Optional[DressInventory]:
    try:
        status_enum = DressStatus(new_status)
    except ValueError:
        raise ValueError(f"Invalid status: {new_status!r}")
    dress = db.query(DressInventory).filter(DressInventory.item_id == item_id).first()
    if dress is None:
        return None
    dress.status = status_enum
    db.flush()
    db.refresh(dress)
    return dress


def add_dress(
    db: Session,
    model_number: str,
    size: str,
    cup_size: str,
    location: str,
    condition: str = "Good",
    notes: Optional[str] = None,
) -> DressInventory:
    try:
        cup_enum = CupSize(cup_size.upper())
    except ValueError:
        valid = ", ".join(e.value for e in CupSize)
        raise ValueError(f"Invalid cup size {cup_size!r}. Valid: {valid}")
    try:
        loc_enum = StorageLocation(location.title())
    except ValueError:
        valid = ", ".join(e.value for e in StorageLocation)
        raise ValueError(f"Invalid location {location!r}. Valid: {valid}")
    try:
        cond_enum = DressCondition(condition.title())
    except ValueError:
        valid = ", ".join(e.value for e in DressCondition)
        raise ValueError(f"Invalid condition {condition!r}. Valid: {valid}")

    dress = DressInventory(
        model_number=model_number,
        size=size,
        cup_size=cup_enum,
        storage_location=loc_enum,
        dress_condition=cond_enum,
        status=DressStatus.IN_STOCK,
        notes=notes,
    )
    db.add(dress)
    db.flush()
    db.refresh(dress)
    return dress


# ---------------------------------------------------------------------------
# Order queries
# ---------------------------------------------------------------------------

def get_all_orders(db: Session, skip: int = 0, limit: int = 100) -> List[ActiveOrder]:
    return db.query(ActiveOrder).offset(skip).limit(limit).all()


def create_order(db: Session, order) -> ActiveOrder:
    db_order = ActiveOrder(**order.model_dump())
    db.add(db_order)
    db.flush()
    db.refresh(db_order)
    return db_order


def link_order_to_dress(
    db: Session, order_id: int, dress_id: int
) -> Optional[ActiveOrder]:
    db_order = db.query(ActiveOrder).filter(ActiveOrder.order_id == order_id).first()
    if db_order:
        db_order.dress_id = dress_id
        db.flush()
        db.refresh(db_order)
    return db_order


def get_orders_filtered(
    db: Session, days: Optional[int] = None
) -> List[ActiveOrder]:
    query = db.query(ActiveOrder)
    if days is not None:
        today = date.today()
        cutoff = today + timedelta(days=days)
        query = query.filter(
            ActiveOrder.wedding_date >= today,
            ActiveOrder.wedding_date <= cutoff,
        )
    return query.order_by(ActiveOrder.wedding_date).all()
