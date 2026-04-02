from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import IdempotencyRecord, Order
from app.schemas.orders import OrderCreate, OrderUpdate


class OrderService:
    def list_orders(self, db: Session, page: int, page_size: int):
        total = db.query(Order).count()
        items = (
            db.query(Order)
            .order_by(Order.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def list_orders_cursor(self, db: Session, limit: int, cursor: int | None):
        query = select(Order).order_by(Order.id.asc()).limit(limit + 1)
        if cursor is not None:
            query = query.where(Order.id > cursor)
        rows = list(db.scalars(query))
        next_cursor = None
        if len(rows) > limit:
            next_cursor = rows[limit - 1].id
            rows = rows[:limit]
        return rows, next_cursor

    def get_order(self, db: Session, order_id: int) -> Order | None:
        return db.get(Order, order_id)

    def create_order(self, db: Session, payload: OrderCreate, client_id: str, idempotency_key: str | None = None) -> Order:
        if idempotency_key:
            existing = db.query(IdempotencyRecord).filter_by(idempotency_key=idempotency_key, client_id=client_id).one_or_none()
            if existing:
                resource_id = int(existing.resource_id)
                order = db.get(Order, resource_id)
                if order:
                    return order

        external_id = f'ord-{client_id}-{db.query(Order).count() + 1}'
        order = Order(
            external_id=external_id,
            customer_name=payload.customer_name,
            item_sku=payload.item_sku,
            quantity=payload.quantity,
            total_cents=payload.total_cents,
            notes=payload.notes,
            status='pending',
        )
        db.add(order)
        db.flush()
        if idempotency_key:
            db.add(IdempotencyRecord(idempotency_key=idempotency_key, client_id=client_id, resource_id=str(order.id)))
        db.commit()
        db.refresh(order)
        return order

    def update_order(self, db: Session, order: Order, payload: OrderUpdate) -> Order:
        order.status = payload.status
        order.notes = payload.notes
        db.commit()
        db.refresh(order)
        return order


order_service = OrderService()
