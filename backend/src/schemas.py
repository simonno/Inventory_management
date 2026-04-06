from pydantic import BaseModel, Field, validator, model_validator, ConfigDict
from datetime import date
from typing import Optional, List
from .models import CupSize, OrderType, StorageLocation, DressCondition, DressStatus

class DressInventoryBase(BaseModel):
    model_number: str
    size: str
    cup_size: CupSize
    is_custom_sewing: bool = False
    storage_location: StorageLocation
    dress_condition: DressCondition
    status: DressStatus
    notes: Optional[str] = None

class DressInventoryCreate(DressInventoryBase):
    pass

class DressInventory(DressInventoryBase):
    model_config = ConfigDict(from_attributes=True)
    item_id: int

class ActiveOrderBase(BaseModel):
    model_number: str
    bride_name: str
    first_measurement_date: date
    wedding_date: date
    size: str
    bust_cm: float
    hips_cm: float
    waist_cm: float
    cup_size: CupSize
    height_cm: float
    is_custom_sewing: bool = False
    order_type: OrderType
    notes: Optional[str] = None
    dress_id: Optional[int] = None

    @model_validator(mode='after')
    def validate_dates(self) -> 'ActiveOrderBase':
        if self.wedding_date <= self.first_measurement_date:
            raise ValueError("Wedding date must be after first measurement date")
        return self

class ActiveOrderCreate(ActiveOrderBase):
    pass

class ActiveOrder(ActiveOrderBase):
    model_config = ConfigDict(from_attributes=True)
    order_id: int
