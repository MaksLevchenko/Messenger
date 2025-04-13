from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from db.models import User, Chat


def select_chat_by_id(chat_id: int):
    """Создаёт запрос находящий чат по его id"""
    q = select()
    q = (
        q.add_columns(Chat)
        .options(selectinload(Chat.messages))
        .options(selectinload(Chat.users))
        .where(Chat.id == chat_id)
    )
    return q


def select_chat_by_ids(user_ids: tuple):
    """Создаёт запрос находящий чат по id пользователей этого чата, если чат не групповой"""
    q = select()

    q = (
        q.add_columns(Chat)
        .options(selectinload(Chat.messages))
        .options(selectinload(Chat.users))
        .join(User, Chat.users)
        .where(User.id == user_ids[0] and User.id == user_ids[1])
        .where(Chat.type_chat)
    )
    q = q.order_by(Chat.updated_at)
    return q


def select_chat_cards(user_id: int):
    """Создаёт запрос находящий чаты пользователя по id пользователя"""
    q = select()

    count = q.add_columns(func.count(Chat.id).label("count"))
    q = (
        q.add_columns(Chat)
        .options(selectinload(Chat.messages))
        .options(selectinload(Chat.users))
        .join(User, Chat.users)
        .where(User.id == user_id)
    )
    q = q.order_by(Chat.updated_at)
    return count, q
