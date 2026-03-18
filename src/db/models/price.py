"""Pydantic model for the `azure.prices` table"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PriceModel(BaseModel):
    """Pydantic model for the `azure.prices` table"""

    id: int
    packaging_code: str
    retail_dollars: float
    retail_unit: str
    wholesale_dollars: Optional[float] = None
    wholesale_unit: Optional[str] = None
    created_at: datetime
