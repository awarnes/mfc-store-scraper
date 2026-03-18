"""Generic GraphQL response wrapper for Shopify requests"""

from typing import TypeVar, Generic, List, Optional, Any

from pydantic import BaseModel

T = TypeVar("T")


class ErrorLocation(BaseModel):
    """The ErrorLocation in a Shopify system error"""

    line: int
    column: int


class Problem(BaseModel):
    """The Problem in a Shopify system error"""

    path: List[str]
    explanation: str


class ErrorExtensions(BaseModel):
    """The ErrorExtensions in a Shopify system error"""

    value: Any
    problems: List[Problem]


class ResponseError(BaseModel):
    """The response error if the query is malformed (almost like a 422)

    Note: This is separate from the UserErrors object which is sent
    when the request is properly formed but invalid
    """

    message: str
    locations: List[ErrorLocation]
    extensions: Optional[ErrorExtensions] = None


class GraphqlResponse(BaseModel, Generic[T]):
    """
    Generic GraphQL response wrapper for any Shopify response

    Example object:
    {
      data: {[mutation/query name]: {...returned data}},
      errors: [{...malformed request errors...}]
    }
    """

    errors: List[ResponseError] = []
    data: T = {}
