"""Pydantic model for the `azure.products` table"""

from pydantic import BaseModel, JsonValue


class ProductModel(BaseModel):
    """Pydantic model for the `azure.products` table"""

    id: int
    shopify_product_id: str
    name: str
    short_description: str
    description: str
    slug: str
    storage_climate: str
    unshippable_regions: JsonValue
    band: JsonValue
    substitutions: JsonValue
    created_at: str
    updated_at: str
