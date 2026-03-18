"""Product options pydantic models"""

from typing import List

from pydantic import BaseModel


class ProductOption(BaseModel):
    """
    ProductOption graphql model
    docs: https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption
    """

    id: str
    optionValues: List[ProductOptionValue]


class ProductOptionValue(BaseModel):
    """
    ProductOptionValue graphql model
    docs: https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOptionValue
    """

    id: str
