from typing import List, Optional

from pydantic import BaseModel


class ProductOption(BaseModel):
    id: str
    optionValues: List[ProductOptionValue]


class ProductOptionValue(BaseModel):
    id: str
