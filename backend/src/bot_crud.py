"""Bot-specific database query functions for the Telegram inventory bot."""

from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from . import models


def get_live_stock(db: Session) -> List[models.DressInventory]:
    return (
        db.query(models.DressInventory)
        .filter(
            models.DressInventory.status.in_(
                [models.DressStatus.IN_STOCK, models.DressStatus.DISPLAY]
            )
        )
        .order_by(models.DressInventory.model_number, models.DressInventory.size)
        .all()
    )


def get_future_stock(db: Session) -> dict:
    future_statuses = [
        models.DressStatus.IN_SEWING,
        models.DressStatus.ABROAD,
        models.DressStatus.OUT_TO_BRIDE,
    ]
    dresses = (
        db.query(models.DressInventory)
        .filter(models.DressInventory.status.in_(future_statuses))
        .order_by(models.DressInventory.status, models.DressInventory.model_number)
        .all()
    )
    new_orders = (
        db.query(models.ActiveOrder)
        .filter(models.ActiveOrder.order_type == models.OrderType.NEW_ORDER)
        .order_by(models.ActiveOrder.wedding_date)
        .all()
    )
    return {"dresses": dresses, "new_orders": new_orders}


def get_dresses_by_model(db: Session, model_number: str) -> List[models.DressInventory]:
    return (
        db.query(models.DressInventory)
        .filter(
            models.DressInventory.model_number.ilike(model_number)
        )
        .order_by(models.DressInventory.size, models.DressInventory.cup_size)
        .all()
    )


def get_orders_filtered(db: Session, days: Optional[int] = None) -> List[models.ActiveOrder]:
    query = db.query(models.ActiveOrder)
    if days is not None:
        today = date.today()
        cutoff = today + timedelta(days=days)
        query = query.filter(
            models.ActiveOrder.wedding_date >= today,
            models.ActiveOrder.wedding_date <= cutoff,
        )
    return query.order_by(models.ActiveOrder.wedding_date).all()


def update_dress_status(
    db: Session, item_id: int, new_status: str
) -> Optional[models.DressInventory]:
    try:
        status_enum = models.DressStatus(new_status)
    except ValueError:
        raise ValueError(f"Invalid status: {new_status}")
    dress = db.query(models.DressInventory).filter(
        models.DressInventory.item_id == item_id
    ).first()
    if dress is None:
        return None
    dress.status = status_enum
    db.commit()
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
) -> models.DressInventory:
    try:
        cup_enum = models.CupSize(cup_size.upper())
    except ValueError:
        valid = ", ".join(e.value for e in models.CupSize)
        raise ValueError(f"Invalid cup size '{cup_size}'. Valid: {valid}")
    try:
        loc_enum = models.StorageLocation(location.title())
    except ValueError:
        valid = ", ".join(e.value for e in models.StorageLocation)
        raise ValueError(f"Invalid location '{location}'. Valid: {valid}")
    try:
        cond_enum = models.DressCondition(condition.title())
    except ValueError:
        valid = ", ".join(e.value for e in models.DressCondition)
        raise ValueError(f"Invalid condition '{condition}'. Valid: {valid}")

    dress = models.DressInventory(
        model_number=model_number,
        size=size,
        cup_size=cup_enum,
        storage_location=loc_enum,
        dress_condition=cond_enum,
        status=models.DressStatus.IN_STOCK,
        notes=notes,
    )
    db.add(dress)
    db.commit()
    db.refresh(dress)
    return dress
