from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.db import Base


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False)
    sku = Column(String, nullable=True, index=True)
    description = Column(Text, nullable=True)
    quantity_on_hand = Column(Float, default=0.0, nullable=False)
    min_quantity = Column(Float, default=0.0, nullable=False)
    unit_of_measure = Column(String, default="unit", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ProcurementRule(Base):
    __tablename__ = "procurement_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    rule_type = Column(String, nullable=False)  # purchase/manufacture
    trigger_quantity = Column(Float, nullable=False)
    order_quantity = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    product = relationship("Product", backref="procurement_rules")


class ProcurementOrder(Base):
    __tablename__ = "procurement_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    order_type = Column(String, nullable=False)  # purchase/manufacture
    quantity = Column(Float, nullable=False)
    status = Column(String, default="draft", nullable=False)  # draft/confirmed/done/cancelled
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    product = relationship("Product", backref="procurement_orders")


class StockMovement(Base):
    __tablename__ = "stock_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    movement_type = Column(String, nullable=False)  # in/out/adjustment
    reference = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    product = relationship("Product", backref="stock_movements")
