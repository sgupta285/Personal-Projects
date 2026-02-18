"""
Category and Customer CRUD routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.database import get_db
from app.models.orm import Category, Customer, Product, gen_id
from app.api.schemas import (
    CategoryCreate, CategoryResponse,
    CustomerCreate, CustomerResponse,
)
from app.services.redis_service import redis_service

# --- Categories ---
cat_router = APIRouter(prefix="/categories", tags=["Categories"])


@cat_router.get("", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    cached = redis_service.cache_get("categories:all")
    if cached:
        return cached

    result = await db.execute(select(Category).order_by(Category.name))
    categories = result.scalars().all()

    response = []
    for cat in categories:
        count_q = select(func.count()).select_from(Product).where(
            Product.category_id == cat.id, Product.is_active == True
        )
        count = (await db.execute(count_q)).scalar() or 0
        response.append(CategoryResponse(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            product_count=count,
            created_at=cat.created_at,
        ))

    redis_service.cache_set("categories:all", [r.model_dump() for r in response], ttl=300)
    return response


@cat_router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    cat = Category(id=gen_id(), name=data.name, description=data.description)
    db.add(cat)
    await db.flush()
    await db.refresh(cat)
    redis_service.cache_delete("categories:all")
    return CategoryResponse(
        id=cat.id, name=cat.name, description=cat.description,
        product_count=0, created_at=cat.created_at,
    )


@cat_router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.id == category_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    count_q = select(func.count()).select_from(Product).where(
        Product.category_id == cat.id, Product.is_active == True
    )
    count = (await db.execute(count_q)).scalar() or 0

    return CategoryResponse(
        id=cat.id, name=cat.name, description=cat.description,
        product_count=count, created_at=cat.created_at,
    )


# --- Customers ---
cust_router = APIRouter(prefix="/customers", tags=["Customers"])


@cust_router.get("", response_model=list[CustomerResponse])
async def list_customers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).order_by(Customer.name).limit(100))
    return [CustomerResponse.model_validate(c) for c in result.scalars().all()]


@cust_router.post("", response_model=CustomerResponse, status_code=201)
async def create_customer(data: CustomerCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Customer).where(Customer.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    customer = Customer(id=gen_id(), email=data.email, name=data.name)
    db.add(customer)
    await db.flush()
    await db.refresh(customer)
    return CustomerResponse.model_validate(customer)


@cust_router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return CustomerResponse.model_validate(customer)
