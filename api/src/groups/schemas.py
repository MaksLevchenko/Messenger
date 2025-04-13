from pydantic import BaseModel, Field


class GroupSchema(BaseModel):
    """Схема группы"""

    title: str = Field(...)
    owner_id: int = Field(...)
    chat_id: int = Field(...)
