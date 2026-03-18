"""Shopify ProductVariant model"""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel

from src.shopify.types.models.money import Money
from src.shopify.types.models.metafield import Metafield


class ProductVariant(BaseModel):
    """
    Shopify product variant model
    docs: https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant
    """

    id: str
    availableForSale: Optional[bool] = None
    barcode: Optional[str] = None
    displayName: Optional[str] = None
    price: Optional[Money] = None
    sku: Optional[str] = None
    title: Optional[str] = None
    metafield: Optional[Metafield] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
