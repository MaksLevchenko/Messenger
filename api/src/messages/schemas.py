from pydantic import BaseModel, Field


class MessageSchema(BaseModel):
    """Схема сообщения"""

    text: str = Field(...)
    chat_id: int = Field(...)
    sender_id: int = Field(...)
    status: bool = Field(default=False)
