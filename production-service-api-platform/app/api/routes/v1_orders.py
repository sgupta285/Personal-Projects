from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.dependencies import AuthContext, require_scope
from app.db import get_db
from app.schemas.common import PaginationMeta
from app.schemas.orders import OrderCreate, OrderRead, OrderUpdate
from app.services.cache import cache
from app.services.orders import order_service

router = APIRouter(prefix='/api/v1/orders', tags=['orders-v1'])


@router.get('')
def list_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    context: AuthContext = Depends(require_scope('orders:read')),
):
    cache_key = f'v1:orders:{page}:{page_size}:{context.client_id}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    items, total = order_service.list_orders(db, page=page, page_size=page_size)
    response = {
        'data': [OrderRead.model_validate(item).model_dump(mode='json') for item in items],
        'meta': PaginationMeta(total=total, page=page, page_size=page_size).model_dump(),
    }
    cache.set(cache_key, response, ttl_seconds=15)
    return response


@router.post('', status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    context: AuthContext = Depends(require_scope('orders:write')),
):
    order = order_service.create_order(db, payload=payload, client_id=context.client_id)
    cache.delete_prefix('v1:orders:')
    return OrderRead.model_validate(order)


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
    return OrderRead.model_validate(order_service.update_order(db, order, payload))
