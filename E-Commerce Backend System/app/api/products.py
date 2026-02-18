"""
Product CRUD with Redis cache-aside for reads.
Cache is invalidated on writes (create, update, delete).
"""

import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.database import get_db
from app.models.orm import Product, Category, gen_id
from app.api.schemas import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
)
from app.services.redis_service import redis_service

router = APIRouter(prefix="/products", tags=["Products"])


def _product_to_response(p: Product) -> ProductResponse:
    return ProductResponse(
        id=p.id,
        name=p.name,
        description=p.description,
        price=p.price,
        stock=p.stock,
        sku=p.sku,
        category_id=p.category_id,
        category_name=p.category.name if p.category else None,
        is_active=p.is_active,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    search: str | None = None,
    in_stock: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List products with filtering, pagination, and cache-aside."""
    cache_key = f"products:list:{page}:{page_size}:{category_id}:{min_price}:{max_price}:{search}:{in_stock}"
    cached = redis_service.cache_get(cache_key)
    if cached:
        return cached

    # Build query with filters
    conditions = [Product.is_active == True]
    if category_id:
        conditions.append(Product.category_id == category_id)
    if min_price is not None:
        conditions.append(Product.price >= min_price)
    if max_price is not None:
        conditions.append(Product.price <= max_price)
    if search:
        conditions.append(Product.name.ilike(f"%{search}%"))
    if in_stock is True:
        conditions.append(Product.stock > 0)

    where = and_(*conditions)

    # Count total
    count_q = select(func.count()).select_from(Product).where(where)
    total = (await db.execute(count_q)).scalar() or 0

    # Fetch page
    offset = (page - 1) * page_size
    q = select(Product).where(where).order_by(Product.name).offset(offset).limit(page_size)
    result = await db.execute(q)
    products = result.scalars().all()

    response = ProductListResponse(
        items=[_product_to_response(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 0,
    )

    redis_service.cache_set(cache_key, response.model_dump(), ttl=120)
    return response


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    """Get single product by ID with caching."""
    cache_key = f"products:{product_id}"
    cached = redis_service.cache_get(cache_key)
    if cached:
        return cached

    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    response = _product_to_response(product)
    redis_service.cache_set(cache_key, response.model_dump())
    return response


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    """Create a new product and invalidate list cache."""
    product = Product(
        id=gen_id(),
        name=data.name,
        description=data.description,
        price=data.price,
        stock=data.stock,
        sku=data.sku,
        category_id=data.category_id,
    )
    db.add(product)
    await db.flush()
    await db.refresh(product)

    redis_service.cache_invalidate_pattern("products:list:*")
    return _product_to_response(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, data: ProductUpdate, db: AsyncSession = Depends(get_db)):
    """Update product and invalidate caches."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    await db.flush()
    await db.refresh(product)

    redis_service.cache_delete(f"products:{product_id}")
    redis_service.cache_invalidate_pattern("products:list:*")
    return _product_to_response(product)


@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: str, db: AsyncSession = Depends(get_db)):
    """Soft-delete product (set is_active=False)."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.is_active = False
    await db.flush()

    redis_service.cache_delete(f"products:{product_id}")
    redis_service.cache_invalidate_pattern("products:list:*")
