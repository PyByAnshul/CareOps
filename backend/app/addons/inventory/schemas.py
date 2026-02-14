from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str
    sku: Optional[str] = None
    description: Optional[str] = None
    quantity_on_hand: float = 0.0
    min_quantity: float = 0.0
    unit_of_measure: str = "unit"


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    min_quantity: Optional[float] = None
    unit_of_measure: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    workspace_id: int
    name: str
    sku: Optional[str]
    description: Optional[str]
    quantity_on_hand: float
    min_quantity: float
    unit_of_measure: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StockMovementCreate(BaseModel):
    product_id: int
    quantity: float
    movement_type: str = Field(..., pattern="^(in|out|adjustment)$")
    reference: Optional[str] = None
    notes: Optional[str] = None


class StockMovementResponse(BaseModel):
    id: int
    workspace_id: int
    product_id: int
    quantity: float
    movement_type: str
    reference: Optional[str]
    notes: Optional[str]
    created_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ProcurementRuleCreate(BaseModel):
    product_id: int
    rule_type: str = Field(..., pattern="^(purchase|manufacture)$")
    trigger_quantity: float
    order_quantity: float


class ProcurementRuleResponse(BaseModel):
    id: int
    workspace_id: int
    product_id: int
    rule_type: str
    trigger_quantity: float
    order_quantity: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProcurementOrderCreate(BaseModel):
    product_id: int
    order_type: str = Field(..., pattern="^(purchase|manufacture)$")
    quantity: float


class ProcurementOrderUpdate(BaseModel):
    status: str = Field(..., pattern="^(draft|confirmed|done|cancelled)$")


class ProcurementOrderResponse(BaseModel):
    id: int
    workspace_id: int
    product_id: int
    order_type: str
    quantity: float
    status: str
    created_by: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
