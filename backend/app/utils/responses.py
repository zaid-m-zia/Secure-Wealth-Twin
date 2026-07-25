from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_api_response(
    *,
    status: str,
    message: str,
    data: Any,
    request_id: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "message": message,
        "data": data,
        "timestamp": utc_now_iso(),
        "request_id": request_id,
    }


def build_error_response(
    *,
    error_code: str,
    description: str,
    possible_solution: str,
    request_id: str,
) -> dict[str, Any]:
    return {
        "timestamp": utc_now_iso(),
        "request_id": request_id,
        "error_code": error_code,
        "description": description,
        "possible_solution": possible_solution,
    }
