"""
ORM models with strategic indexes for read-heavy e-commerce workloads.
Indexes target the most common query patterns: product listing, category filtering,
order lookup by user, and inventory checks.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Integer, Text, Boolean,
    ForeignKey, DateTime, Index, Enum as SAEnum,
)
from sqlalchemy.orm import relationship
import enum

from app.models.database import Base


def gen_id() -> str:
    return str(uuid.uuid4())


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", back_populates="category", lazy="selectin")


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    sku = Column(String(50), unique=True, nullable=False)
    category_id = Column(String, ForeignKey("categories.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="products", lazy="selectin")
    order_items = relationship("OrderItem", back_populates="product", lazy="noload")

    # Strategic indexes for common query patterns
    __table_args__ = (
        Index("idx_product_category", "category_id", "is_active"),
        Index("idx_product_price", "price"),
        Index("idx_product_active_name", "is_active", "name"),
        Index("idx_product_sku", "sku"),
        Index("idx_product_stock", "stock"),
    )


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, default=gen_id)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="customer", lazy="noload")


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=gen_id)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    status = Column(String(20), default=OrderStatus.PENDING.value)
    total = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="orders", lazy="selectin")
    items = relationship("OrderItem", back_populates="order", lazy="selectin")

    __table_args__ = (
        Index("idx_order_customer", "customer_id", "created_at"),
        Index("idx_order_status", "status"),
        Index("idx_order_created", "created_at"),
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String, primary_key=True, default=gen_id)
    order_id = Column(String, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items", lazy="selectin")

    __table_args__ = (
        Index("idx_order_item_order", "order_id"),
        Index("idx_order_item_product", "product_id"),
    )
