from typing import TYPE_CHECKING
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db import Base
from db.models.mixins.dates import CreatedAtMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from db.models import Chat, User


class Message(CreatedAtMixin, UpdatedAtMixin, Base):
    """Модель сообщения"""

    text = Column(String, nullable=False)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"))
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status = Column(Boolean, default=False)

    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
    sender: Mapped["User"] = relationship("User", back_populates="messages")
