"""
Shopify monetary value:
A monetary value string without a currency symbol or code. Example value: "100.57".
https://shopify.dev/docs/api/admin-graphql/latest/scalars/Money
"""

from typing import Annotated
from pydantic import StringConstraints

Money = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, strict=True, pattern=r"^[0-9]+\.[0-9]{2}$"
    ),
]
