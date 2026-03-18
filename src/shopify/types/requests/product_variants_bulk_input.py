"""Shopify models for the productVariantsBulkCreate/Update mutations"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from src.shopify.types.models.money import Money
from src.shopify.types.models.product import Product
from src.shopify.types.models.product_variant import ProductVariant
from src.shopify.types.requests.user_errors import UserErrors
from src.shopify.types.requests.graphql_response import GraphqlResponse
from src.shopify.types.models.metafield import Metafield


class ProductVariantsBulkCreateStrategy(str, Enum):
    """
    The strategy defines which behavior the mutation should observe,
    such as whether to keep or delete the standalone variant
    (when product has only a single or default variant) when
    creating new variants in bulk.
    """

    DEFAULT = "DEFAULT"
    PRESERVE_STANDALONE_VARIANT = "PRESERVE_STANDALONE_VARIANT"
    REMOVE_STANDALONE_VARIANT = "REMOVE_STANDALONE_VARIANT"


class ProductVariantInventoryPolicy(str, Enum):
    """
    Whether customers are allowed to place an order for the
    variant when it's out of stock. Defaults to DENY.
    """

    CONTINUE_SELLING = "CONTINUE"
    DENY = "DENY"


class InventoryItemInput(BaseModel):
    """The inventory item associated with the variant, used for unit cost."""

    cost: Optional[Money] = None
    countryCodeOfOrigin: Optional[str] = None
    requiresShipping: bool = True
    sku: str
    tracked: bool = True


class VariantOptionValueInput(BaseModel):
    """VariantOptionValueInput model

    Generally, we won't need to add options beyond the size of the product,
    but can use this for other option types as well
    """

    optionName: str = "Size"
    name: str


class ProductVariantsBulkInput(BaseModel):
    """
    Product variants to be created or updated
    docs: https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ProductVariantsBulkInput
    """

    barcode: Optional[str] = ""
    compareAtPrice: Optional[Money] = None
    id: str = None
    inventoryItem: Optional[InventoryItemInput] = {}
    inventoryPolicy: ProductVariantInventoryPolicy
    optionValues: List[VariantOptionValueInput]
    mediaId: str
    price: Money
    taxable: bool = False
    metafields: List[Metafield]


class ProductVariantsBulkData(BaseModel):
    """Graphql response helper model"""

    product: Optional[Product] = None
    productVariants: List[ProductVariant] = []
    userErrors: List[UserErrors] = []


class ProductVariantsBulkCreatePayload(BaseModel):
    """
    Payload returned after calling the productVariantsBulkCreate mutation
    """

    productVariantsBulkCreate: ProductVariantsBulkData


class ProductVariantsBulkUpdatePayload(BaseModel):
    """
    Payload returned after calling the productVariantsBulkUpdate mutation
    """

    productVariantsBulkUpdate: ProductVariantsBulkData


ProductVariantsBulkCreateResponse = GraphqlResponse[ProductVariantsBulkCreatePayload]
ProductVariantsBulkUpdateResponse = GraphqlResponse[ProductVariantsBulkUpdatePayload]
