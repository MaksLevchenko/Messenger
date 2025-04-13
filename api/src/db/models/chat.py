from typing import TYPE_CHECKING, List
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship, Mapped
from db import Base
from db.models.mixins.dates import CreatedAtMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from db.models import Message, User, ChatGroup


class Chat(CreatedAtMixin, UpdatedAtMixin, Base):
    """Модель чата"""

    title = Column(String, nullable=False)
    type_chat = Column(Boolean, default=False)

    messages: Mapped[List["Message"]] = relationship("Message", back_populates="chat")

    group: Mapped["ChatGroup"] = relationship("ChatGroup", back_populates="chat")
    users: Mapped[List["User"]] = relationship(
        "User", secondary="association_users_chat", back_populates="chats"
    )
