from typing import TypeVar, Generic, List, Optional, Any

from pydantic import BaseModel

T = TypeVar("T")


class ErrorLocation(BaseModel):
    line: int
    column: int


class Problem(BaseModel):
    path: List[str]
    explanation: str


class ErrorExtensions(BaseModel):
    value: Any
    problems: List[Problem]


class ResponseError(BaseModel):
    message: str
    locations: List[ErrorLocation]
    extensions: Optional[ErrorExtensions] = None


class GraphqlResponse(BaseModel, Generic[T]):
    errors: List[ResponseError] = []
    data: T = {}
