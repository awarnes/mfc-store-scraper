"""UserErrors model from the Shopify GraphQL response"""

from typing import List

from pydantic import BaseModel


class UserErrors(BaseModel):
    """UserErrors from the Shopify GraphQL response"""

    field: List[str]

    message: str
