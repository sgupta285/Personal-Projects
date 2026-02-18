from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


# --- Products ---
class ProductCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: str = ""
    price: float = Field(..., gt=0)
    stock: int = Field(0, ge=0)
    sku: str = Field(..., max_length=50)
    category_id: str | None = None


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    category_id: str | None = None
    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    stock: int
    sku: str
    category_id: str | None
    category_name: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    pages: int


# --- Categories ---
class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = ""


class CategoryResponse(BaseModel):
    id: str
    name: str
    description: str
    product_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Customers ---
class CustomerCreate(BaseModel):
    email: str = Field(..., max_length=255)
    name: str = Field(..., max_length=200)


class CustomerResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Orders ---
class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer_id: str
    items: list[OrderItemCreate] = Field(..., min_length=1)


class OrderItemResponse(BaseModel):
    id: str
    product_id: str
    product_name: str | None = None
    quantity: int
    unit_price: float

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: str
    customer_id: str
    customer_name: str | None = None
    status: str
    total: float
    items: list[OrderItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int
    page: int
    page_size: int


# --- Health ---
class HealthResponse(BaseModel):
    status: str
    database: str
    cache: str
    version: str
    uptime_seconds: float
