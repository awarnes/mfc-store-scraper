from pydantic import BaseModel


class OptionUpdateInput(BaseModel):
    id: str
