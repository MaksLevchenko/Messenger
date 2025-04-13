from typing import TYPE_CHECKING, List
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db import Base
from db.models.mixins.dates import CreatedAtMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from db.models import User, Chat, association_users_group


class ChatGroup(CreatedAtMixin, UpdatedAtMixin, Base):
    """Модель группы"""

    id = Column(Integer, primary_key=True, index=True, unique=True, nullable=False)
    title = Column(String, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"))

    chat: Mapped["Chat"] = relationship("Chat", back_populates="group")
    owner: Mapped["User"] = relationship("User", back_populates="group_main")
    users: Mapped[List["User"]] = relationship(
        "User", secondary="association_users_group", back_populates="groups"
    )
