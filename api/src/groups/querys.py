from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from db.models import User, Chat, ChatGroup


def select_all_groups_cards():
    """Создаёт запрос находящий все группы"""
    q = select()

    count = q.add_columns(func.count(ChatGroup.id).label("count"))
    q = (
        q.add_columns(ChatGroup)
        .options(selectinload(ChatGroup.chat))
        .options(selectinload(ChatGroup.users))
        .join(User, ChatGroup.users)
    )
    q = q.order_by(ChatGroup.updated_at)
    return count, q


def select_user_groups_cards(user_id: int):
    """Создаёт запрос находящий группы пользователя"""
    q = select()

    count = q.add_columns(func.count(ChatGroup.id).label("count"))
    q = (
        q.add_columns(ChatGroup)
        .options(selectinload(ChatGroup.chat))
        .options(selectinload(ChatGroup.users))
        .join(User, ChatGroup.users)
        .where(User.id == user_id)
    )
    q = q.order_by(ChatGroup.updated_at)
    return count, q


def select_group_by_id(group_id: int):
    """Создаёт запрос находящий группу по её id"""
    q = select()
    q = (
        q.add_columns(ChatGroup)
        .options(selectinload(ChatGroup.chat))
        .options(selectinload(ChatGroup.users))
        .join(Chat, ChatGroup.chat)
        .where(ChatGroup.id == group_id)
    )
    return q
