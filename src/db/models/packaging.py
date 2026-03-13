"""Pydantic model for the `azure.packaging` table"""

from pydantic import BaseModel, JsonValue


class PackagingModel(BaseModel):
    """Pydantic model for the `azure.packaging` table"""

    id: int
    products_id: int
    code: str
    shopify_variant_id: str
    size: str
    weight: JsonValue
    stock: int
    rewards_enabled: bool
    freight_handling_required: bool
    tags: JsonValue
    primary_category: int
    favorites: int
    next_purchase_arrival: str
    created_at: str
    updated_at: str
