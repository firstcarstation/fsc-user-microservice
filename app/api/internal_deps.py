"""Service-to-service authentication (Order / Vehicle MS calling User MS)."""

from typing import Annotated, Optional

from fastapi import Header

from app.core.config import settings
from app.core.exceptions import AppException


def require_internal_api_key(
    x_internal_api_key: Annotated[Optional[str], Header(alias="X-Internal-Api-Key")] = None,
) -> bool:
    expected = settings.INTERNAL_API_KEY.strip()
    if not expected:
        return True
    if not x_internal_api_key or x_internal_api_key != expected:
        raise AppException("Unauthorized", status_code=401)
    return True
