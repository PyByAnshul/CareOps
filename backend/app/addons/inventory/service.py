from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.addons.inventory.models import (
    ProcurementOrder,
    ProcurementRule,
    Product,
    StockMovement,
)
from app.addons.inventory.schemas import (
    ProcurementOrderCreate,
    ProcurementRuleCreate,
    ProductCreate,
    ProductUpdate,
    StockMovementCreate,
)


class InventoryService:
    def __init__(self, db: Session):
        self.db = db

    def list_products(self, workspace_id: int) -> List[Product]:
        return self.db.query(Product).filter(Product.workspace_id == workspace_id).all()

    def get_product(self, product_id: int, workspace_id: int) -> Product:
        product = self.db.query(Product).filter(
            Product.id == product_id, Product.workspace_id == workspace_id
        ).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    def create_product(self, data: ProductCreate, workspace_id: int) -> Product:
        product = Product(**data.model_dump(), workspace_id=workspace_id)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update_product(self, product_id: int, data: ProductUpdate, workspace_id: int) -> Product:
        product = self.get_product(product_id, workspace_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(product, key, value)
        self.db.commit()
        self.db.refresh(product)
        return product

    def create_stock_movement(
        self, data: StockMovementCreate, workspace_id: int, user_id: int
    ) -> StockMovement:
        product = self.get_product(data.product_id, workspace_id)
        
        movement = StockMovement(
            **data.model_dump(), workspace_id=workspace_id, created_by=user_id
        )
        self.db.add(movement)
        
        if data.movement_type == "in":
            product.quantity_on_hand += data.quantity
        elif data.movement_type == "out":
            if product.quantity_on_hand < data.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient stock"
                )
            product.quantity_on_hand -= data.quantity
        elif data.movement_type == "adjustment":
            product.quantity_on_hand = data.quantity
        
        self.db.commit()
        self.db.refresh(movement)
        
        self._check_procurement_rules(product)
        
        return movement

    def list_stock_movements(self, workspace_id: int, product_id: Optional[int] = None) -> List[StockMovement]:
        query = self.db.query(StockMovement).filter(StockMovement.workspace_id == workspace_id)
        if product_id:
            query = query.filter(StockMovement.product_id == product_id)
        return query.order_by(StockMovement.created_at.desc()).all()

    def create_procurement_rule(self, data: ProcurementRuleCreate, workspace_id: int) -> ProcurementRule:
        self.get_product(data.product_id, workspace_id)
        rule = ProcurementRule(**data.model_dump(), workspace_id=workspace_id)
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def list_procurement_rules(self, workspace_id: int) -> List[ProcurementRule]:
        return self.db.query(ProcurementRule).filter(
            ProcurementRule.workspace_id == workspace_id
        ).all()

    def create_procurement_order(
        self, data: ProcurementOrderCreate, workspace_id: int, user_id: int
    ) -> ProcurementOrder:
        self.get_product(data.product_id, workspace_id)
        order = ProcurementOrder(
            **data.model_dump(), workspace_id=workspace_id, created_by=user_id
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def update_procurement_order(
        self, order_id: int, new_status: str, workspace_id: int
    ) -> ProcurementOrder:
        order = self.db.query(ProcurementOrder).filter(
            ProcurementOrder.id == order_id, ProcurementOrder.workspace_id == workspace_id
        ).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
        order.status = new_status
        if new_status == "done":
            from datetime import datetime
            order.completed_at = datetime.utcnow()
            product = self.get_product(order.product_id, workspace_id)
            product.quantity_on_hand += order.quantity
        
        self.db.commit()
        self.db.refresh(order)
        return order

    def list_procurement_orders(self, workspace_id: int) -> List[ProcurementOrder]:
        return self.db.query(ProcurementOrder).filter(
            ProcurementOrder.workspace_id == workspace_id
        ).order_by(ProcurementOrder.created_at.desc()).all()

    def _check_procurement_rules(self, product: Product):
        rules = self.db.query(ProcurementRule).filter(
            ProcurementRule.product_id == product.id,
            ProcurementRule.is_active == True
        ).all()
        
        for rule in rules:
            if product.quantity_on_hand <= rule.trigger_quantity:
                existing_order = self.db.query(ProcurementOrder).filter(
                    ProcurementOrder.product_id == product.id,
                    ProcurementOrder.status.in_(["draft", "confirmed"])
                ).first()
                
                if not existing_order:
                    order = ProcurementOrder(
                        workspace_id=product.workspace_id,
                        product_id=product.id,
                        order_type=rule.rule_type,
                        quantity=rule.order_quantity,
                        status="draft"
                    )
                    self.db.add(order)
                    self.db.commit()
