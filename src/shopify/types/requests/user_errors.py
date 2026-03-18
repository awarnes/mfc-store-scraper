from typing import List

from pydantic import BaseModel


class UserErrors(BaseModel):
    """User errors from the Shopify GraphQL response"""

    field: List[str]

    message: str
