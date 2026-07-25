from contextvars import ContextVar
from uuid import uuid4

request_id_context: ContextVar[str] = ContextVar("request_id", default="")


def new_request_id() -> str:
    return uuid4().hex


def set_request_id(request_id: str) -> None:
    request_id_context.set(request_id)


def get_request_id() -> str:
    current = request_id_context.get()
    return current or "-"
