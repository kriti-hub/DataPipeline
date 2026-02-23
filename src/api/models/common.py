"""Shared Pydantic types for pagination, error responses, and common fields."""

from pydantic import BaseModel, ConfigDict


class PaginationMeta(BaseModel):
    """Pagination metadata included in every paginated response."""

    model_config = ConfigDict(strict=True)

    page: int
    page_size: int
    total_records: int
    total_pages: int


class ErrorDetail(BaseModel):
    """Structured error detail."""

    model_config = ConfigDict(strict=True)

    code: int
    message: str
    details: str | None = None


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    model_config = ConfigDict(strict=True)

    error: ErrorDetail
