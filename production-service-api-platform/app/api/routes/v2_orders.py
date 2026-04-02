from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.dependencies import AuthContext, require_scope
from app.db import get_db
from app.schemas.common import AuditStamp, PaginationMeta
from app.schemas.orders import OrderCreate, OrderRead, OrderReadV2, OrderUpdate
from app.services.cache import cache
from app.services.orders import order_service

router = APIRouter(prefix='/api/v2/orders', tags=['orders-v2'])


def as_v2(order) -> dict:
    base = OrderRead.model_validate(order).model_dump()
    return OrderReadV2(
        **base,
        links={'self': f'/api/v2/orders/{order.id}'},
        audit=AuditStamp(created_at=order.created_at, updated_at=order.updated_at),
    ).model_dump(mode='json')


@router.get('')
def list_orders(
    cursor: int | None = Query(default=None, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    context: AuthContext = Depends(require_scope('orders:read')),
):
    cache_key = f'v2:orders:{cursor}:{limit}:{context.client_id}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    items, next_cursor = order_service.list_orders_cursor(db, limit=limit, cursor=cursor)
    response = {
        'data': [as_v2(order) for order in items],
        'meta': PaginationMeta(total=len(items), next_cursor=str(next_cursor) if next_cursor else None).model_dump(),
    }
    cache.set(cache_key, response, ttl_seconds=15)
    return response


@router.get('/{order_id}')
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    context: AuthContext = Depends(require_scope('orders:read')),
):
    order = order_service.get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail={'code': 'not_found', 'message': 'Order not found'})
    return as_v2(order)


@router.post('', status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    idempotency_key: str | None = Header(default=None, alias='Idempotency-Key'),
    db: Session = Depends(get_db),
    context: AuthContext = Depends(require_scope('orders:write')),
):
    order = order_service.create_order(
        db,
        payload=payload,
        client_id=context.client_id,
        idempotency_key=idempotency_key,
    )
    cache.delete_prefix('v1:orders:')
    cache.delete_prefix('v2:orders:')
    return as_v2(order)


@router.patch('/{order_id}')
def update_order(
    order_id: int,
    payload: OrderUpdate,
    db: Session = Depends(get_db),
    context: AuthContext = Depends(require_scope('orders:write')),
):
    order = order_service.get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail={'code': 'not_found', 'message': 'Order not found'})
    cache.delete_prefix('v1:orders:')
    cache.delete_prefix('v2:orders:')
    return as_v2(order_service.update_order(db, order, payload))
