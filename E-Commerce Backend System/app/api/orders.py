"""
Order management with stock validation and transactional integrity.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.database import get_db
from app.models.orm import Order, OrderItem, Product, Customer, gen_id
from app.api.schemas import (
    OrderCreate, OrderResponse, OrderItemResponse, OrderListResponse,
)
from app.services.redis_service import redis_service

router = APIRouter(prefix="/orders", tags=["Orders"])


def _order_to_response(order: Order) -> OrderResponse:
    items = []
    for item in (order.items or []):
        items.append(OrderItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product.name if item.product else None,
            quantity=item.quantity,
            unit_price=item.unit_price,
        ))
    return OrderResponse(
        id=order.id,
        customer_id=order.customer_id,
        customer_name=order.customer.name if order.customer else None,
        status=order.status,
        total=order.total,
        items=items,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(data: OrderCreate, db: AsyncSession = Depends(get_db)):
    """
    Create order with stock validation.
    Decrements product stock atomically and calculates total.
    """
    # Validate customer
    cust = await db.execute(select(Customer).where(Customer.id == data.customer_id))
    customer = cust.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    order_id = gen_id()
    total = 0.0
    order_items = []

    for item_data in data.items:
        result = await db.execute(
            select(Product).where(Product.id == item_data.product_id, Product.is_active == True)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item_data.product_id} not found")
        if product.stock < item_data.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}: available={product.stock}, requested={item_data.quantity}",
            )

        # Decrement stock
        product.stock -= item_data.quantity
        line_total = product.price * item_data.quantity
        total += line_total

        order_items.append(OrderItem(
            id=gen_id(),
            order_id=order_id,
            product_id=product.id,
            quantity=item_data.quantity,
            unit_price=product.price,
        ))

    order = Order(
        id=order_id,
        customer_id=data.customer_id,
        total=round(total, 2),
        status="pending",
    )
    db.add(order)
    for oi in order_items:
        db.add(oi)

    await db.flush()
    await db.refresh(order)

    # Invalidate product caches (stock changed)
    redis_service.cache_invalidate_pattern("products:*")

    return _order_to_response(order)


@router.get("", response_model=OrderListResponse)
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    customer_id: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List orders with optional filters."""
    q = select(Order)
    count_q = select(func.count()).select_from(Order)

    if customer_id:
        q = q.where(Order.customer_id == customer_id)
        count_q = count_q.where(Order.customer_id == customer_id)
    if status:
        q = q.where(Order.status == status)
        count_q = count_q.where(Order.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    q = q.order_by(Order.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(q)
    orders = result.scalars().all()

    return OrderListResponse(
        items=[_order_to_response(o) for o in orders],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db: AsyncSession = Depends(get_db)):
    """Get order by ID."""
    cache_key = f"orders:{order_id}"
    cached = redis_service.cache_get(cache_key)
    if cached:
        return cached

    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    response = _order_to_response(order)
    redis_service.cache_set(cache_key, response.model_dump(), ttl=60)
    return response


@router.patch("/{order_id}/status")
async def update_order_status(order_id: str, status: str, db: AsyncSession = Depends(get_db)):
    """Update order status."""
    valid = {"pending", "confirmed", "shipped", "delivered", "cancelled"}
    if status not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid}")

    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Restore stock if cancelling
    if status == "cancelled" and order.status != "cancelled":
        for item in order.items:
            prod_result = await db.execute(select(Product).where(Product.id == item.product_id))
            product = prod_result.scalar_one_or_none()
            if product:
                product.stock += item.quantity
        redis_service.cache_invalidate_pattern("products:*")

    order.status = status
    await db.flush()

    redis_service.cache_delete(f"orders:{order_id}")
    return {"id": order_id, "status": status}
