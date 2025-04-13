from db import Base

from sqlalchemy import Table, Column, ForeignKey, UniqueConstraint, Integer


association_users_group = Table(
    "association_users_group",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("users.id"), nullable=False),
    Column("group_id", ForeignKey("chatgroups.id"), nullable=False),
    UniqueConstraint("user_id", "group_id", name="idx_group_user"),
)

association_users_chat = Table(
    "association_users_chat",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("users.id"), nullable=False),
    Column("chat_id", ForeignKey("chats.id"), nullable=False),
    UniqueConstraint("user_id", "chat_id", name="idx_chat_user"),
)
