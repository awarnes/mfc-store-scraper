from pydantic import BaseModel

from enum import Enum


class MediaContentType(str, Enum):
    """
    The media content type.
    """

    external_video = "EXTERNAL_VIDEO"
    image = "IMAGE"
    model_3d = "MODEL_3D"
    video = "VIDEO"


class CreateMediaInput(BaseModel):
    """
    The input fields required to create a media object.
    docs: https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CreateMediaInput
    """

    alt: str = ""
    mediaContentType: MediaContentType
    originalSource: str
