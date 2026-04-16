"""ORM models and enums for the bridal inventory system."""

from sqlalchemy import Column, Integer, String, Date, Boolean, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()


class CupSize(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class OrderType(str, enum.Enum):
    STOCK_BASED = "Stock-based"
    NEW_ORDER = "New Order"
    TRUNK_SHOW = "Trunk-show"


class StorageLocation(str, enum.Enum):
    TEL_AVIV = "Tel Aviv"
    ASHDOD = "Ashdod"
    ABROAD = "Abroad"


class DressCondition(str, enum.Enum):
    GOOD = "Good"
    LAUNDRY_DAMAGE = "Laundry Damage"
    REPLACE_TOP = "Replace Top"
    REPLACE_SKIRT = "Replace Skirt"


class DressStatus(str, enum.Enum):
    IN_STOCK = "In Stock"
    DISPLAY = "Display"
    ABROAD = "Abroad"
    IN_SEWING = "In Sewing"
    OUT_TO_BRIDE = "Out to Bride"


class DressInventory(Base):
    __tablename__ = "dress_inventory"

    item_id = Column(Integer, primary_key=True, index=True)
    model_number = Column(String)
    size = Column(String)
    cup_size = Column(Enum(CupSize))
    is_custom_sewing = Column(Boolean, default=False)
    storage_location = Column(Enum(StorageLocation))
    dress_condition = Column(Enum(DressCondition))
    status = Column(Enum(DressStatus))
    notes = Column(String, nullable=True)

    orders = relationship("ActiveOrder", back_populates="dress")


class ActiveOrder(Base):
    __tablename__ = "active_orders"

    order_id = Column(Integer, primary_key=True, index=True)
    model_number = Column(String)
    bride_name = Column(String)
    first_measurement_date = Column(Date)
    wedding_date = Column(Date)
    size = Column(String)
    bust_cm = Column(Float)
    hips_cm = Column(Float)
    waist_cm = Column(Float)
    cup_size = Column(Enum(CupSize))
    height_cm = Column(Float)
    is_custom_sewing = Column(Boolean, default=False)
    order_type = Column(Enum(OrderType))
    notes = Column(String, nullable=True)

    dress_id = Column(Integer, ForeignKey("dress_inventory.item_id"), nullable=True)
    dress = relationship("DressInventory", back_populates="orders")
