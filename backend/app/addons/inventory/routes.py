from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.addons.inventory.schemas import (
    ProcurementOrderCreate,
    ProcurementOrderResponse,
    ProcurementOrderUpdate,
    ProcurementRuleCreate,
    ProcurementRuleResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    StockMovementCreate,
    StockMovementResponse,
)
from app.addons.inventory.service import InventoryService
from app.addons.users.models import User
from app.addons.workspace.models import Workspace
from app.core.db import get_db
from app.core.security.deps import get_current_workspace, require_active_user
from app.core.security.permissions import PermissionChecker

router = APIRouter(tags=["inventory"])


@router.get("/products", response_model=List[ProductResponse])
def list_products(
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(PermissionChecker("inventory.read")),
    db: Session = Depends(get_db),
):
    service = InventoryService(db)
    return service.list_products(workspace.id)


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(PermissionChecker("inventory.write")),
    db: Session = Depends(get_db),
):
    service = InventoryService(db)
    return service.create_product(data, workspace.id)


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(PermissionChecker("inventory.read")),
    db: Session = Depends(get_db),
):
    service = InventoryService(db)
    return service.get_product(product_id, workspace.id)


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(PermissionChecker("inventory.write")),
    db: Session = Depends(get_db),
):
    service = InventoryService(db)
    return service.update_product(product_id, data, workspace.id)


@router.post("/stock-movements", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
def create_stock_movement(
    data: StockMovementCreate,
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(PermissionChecker("inventory.write")),
    db: Session = Depends(get_db),
):
    service = InventoryService(db)
    return service.create_stock_movement(data, workspace.id, current_user.id)


@router.get("/stock-movements", response_model=List[StockMovementResponse])
def list_stock_movements(
    product_id: Optional[int] = None,
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(PermissionChecker("inventory.read")),
    db: Session = Depends(get_db),
):
    service = InventoryService(db)
    return service.list_stock_movements(workspace.id, product_id)


@router.post("/procurement-rules", response_model=ProcurementRuleResponse, status_code=status.HTTP_201_CREATED)
def create_procurement_rule(
    data: ProcurementRuleCreate,
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(PermissionChecker("inventory.write")),
    db: Session = Depends(get_db),
):
    service = InventoryService(db)
    return service.create_procurement_rule(data, workspace.id)


@router.get("/procurement-rules", response_model=List[ProcurementRuleResponse])
def list_procurement_rules(
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(PermissionChecker("inventory.read")),
    db: Session = Depends(get_db),
):
    service = InventoryService(db)
    return service.list_procurement_rules(workspace.id)


@router.post("/procurement-orders", response_model=ProcurementOrderResponse, status_code=status.HTTP_201_CREATED)
def create_procurement_order(
    data: ProcurementOrderCreate,
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(PermissionChecker("inventory.write")),
    db: Session = Depends(get_db),
):
    service = InventoryService(db)
    return service.create_procurement_order(data, workspace.id, current_user.id)


@router.put("/procurement-orders/{order_id}", response_model=ProcurementOrderResponse)
def update_procurement_order(
    order_id: int,
    data: ProcurementOrderUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(PermissionChecker("inventory.write")),
    db: Session = Depends(get_db),
):
    service = InventoryService(db)
    return service.update_procurement_order(order_id, data.status, workspace.id)


@router.get("/procurement-orders", response_model=List[ProcurementOrderResponse])
def list_procurement_orders(
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(PermissionChecker("inventory.read")),
    db: Session = Depends(get_db),
):
    service = InventoryService(db)
    return service.list_procurement_orders(workspace.id)
