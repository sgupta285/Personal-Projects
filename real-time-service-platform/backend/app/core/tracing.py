from contextvars import ContextVar
from uuid import uuid4

correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    current = correlation_id_ctx.get()
    if current:
        return current
    new_value = str(uuid4())
    correlation_id_ctx.set(new_value)
    return new_value


def set_correlation_id(value: str) -> None:
    correlation_id_ctx.set(value)
