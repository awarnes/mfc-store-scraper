from pydantic import BaseModel
from typing import List, Optional

from src.shopify.types.models.product import Product, ProductStatus
from src.shopify.types.requests.user_errors import UserErrors
from src.shopify.types.requests.graphql_response import GraphqlResponse
from src.shopify.types.models.metafield import Metafield


class OptionValueCreateInput(BaseModel):
    """
    Values associated with the option.
    """

    name: str


class OptionCreateInput(BaseModel):
    """
    A list of product options and option values. Maximum product options: three. There's no limit on the number of option values.
    """

    name: str
    values: List[OptionValueCreateInput] = [OptionValueCreateInput(name="Default")]


class ProductCreateInput(BaseModel):
    """
    The attributes of the new product.
    docs: https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ProductCreateInput
    """

    category: str
    collectionsToJoin: List[str] = []
    descriptionHtml: str
    handle: str
    productOptions: List[OptionCreateInput] = []
    productType: str = ""
    status: ProductStatus
    tags: List[str] = []
    title: str
    vendor: str
    metafields: List[Metafield]


class ProductCreateData(BaseModel):
    product: Optional[Product] = {}
    userErrors: List[UserErrors]


class ProductCreatePayload(BaseModel):
    """
    Returned attributes from the ProductCreate mutation
    """

    productCreate: ProductCreateData


ProductCreateResponse = GraphqlResponse[ProductCreatePayload]
