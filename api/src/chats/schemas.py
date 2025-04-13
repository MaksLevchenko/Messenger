from pydantic import BaseModel, Field


class ChatSchema(BaseModel):
    """Схема чата"""

    title: str = Field(..., min_length=2)
    type_chat: bool = Field(
        ...,
    )
