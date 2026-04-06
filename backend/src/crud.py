from sqlalchemy.orm import Session
from . import models, schemas

# Dress Inventory CRUD
def get_dress_inventory(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DressInventory).offset(skip).limit(limit).all()

def create_dress_inventory(db: Session, dress: schemas.DressInventoryCreate):
    db_dress = models.DressInventory(**dress.model_dump())
    db.add(db_dress)
    db.commit()
    db.refresh(db_dress)
    return db_dress

# Active Orders CRUD
def get_active_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ActiveOrder).offset(skip).limit(limit).all()

def create_active_order(db: Session, order: schemas.ActiveOrderCreate):
    db_order = models.ActiveOrder(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def link_order_to_dress(db: Session, order_id: int, dress_id: int):
    db_order = db.query(models.ActiveOrder).filter(models.ActiveOrder.order_id == order_id).first()
    if db_order:
        db_order.dress_id = dress_id
        db.commit()
        db.refresh(db_order)
    return db_order
