"""Pydantic model for the `azure.media` table"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MediaModel(BaseModel):
    """Pydantic model for the `azure.media` table"""

    id: int
    packaging_code: str
    original_url: str
    file_name: str | None = None
    shopify_media_id: str | None = None
    shopify_updated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
