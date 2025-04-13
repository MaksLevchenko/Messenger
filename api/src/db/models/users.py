from typing import TYPE_CHECKING, List
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Mapped


from db import Base
from db.models.mixins.dates import CreatedAtMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from db.models import Message, ChatGroup, Chat, association_users_group


class User(CreatedAtMixin, UpdatedAtMixin, Base):
    """Модель пользователя"""

    id = Column(Integer, primary_key=True, index=True, unique=True, nullable=False)
    name = Column(String(20), nullable=False)
    email = Column(String(40), nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)

    messages: Mapped["Message"] = relationship("Message", back_populates="sender")
    group_main: Mapped[List["ChatGroup"]] = relationship(
        "ChatGroup",
        secondary="association_users_group",
        back_populates="owner",
        overlaps="users",
    )
    groups: Mapped[List["ChatGroup"]] = relationship(
        "ChatGroup",
        secondary="association_users_group",
        back_populates="users",
        overlaps="group_main",
    )
    chats: Mapped[List["Chat"]] = relationship(
        "Chat",
        secondary="association_users_chat",
        back_populates="users",
        overlaps="group_main",
    )
