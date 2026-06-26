from pydantic import BaseModel
from typing import Any


class ApiResponse(BaseModel):
    ok: bool
    message: str | None = None
    data: Any | None = None


class ListResponse(BaseModel):
    ok: bool = True
    items: list[Any] = []
    total: int | None = None
