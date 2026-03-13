"""Pydantic model for the `azure.prices` table"""

from pydantic import BaseModel


class PriceModel(BaseModel):
    """Pydantic model for the `azure.prices` table"""

    id: int
    packaging_code: str
    retail_dollars: float
    retail_unit: str
    wholesale_dollars: float
    wholesale_unit: str
    created_at: str
