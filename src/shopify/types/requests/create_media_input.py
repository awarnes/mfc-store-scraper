"""Shopify CreateMediaInput graphql model"""

from enum import Enum

from pydantic import BaseModel


class MediaContentType(str, Enum):
    """
    The media content type.
    """

    EXTERNAL_VIDEO = "EXTERNAL_VIDEO"
    IMAGE = "IMAGE"
    MODEL_3D = "MODEL_3D"
    VIDEO = "VIDEO"


class CreateMediaInput(BaseModel):
    """
    The input fields required to create a media object.
    docs: https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CreateMediaInput
    """

    alt: str = ""
    mediaContentType: MediaContentType
    originalSource: str
