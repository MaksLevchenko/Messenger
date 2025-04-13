from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from db.models import Message, Chat, ChatGroup


def select_message_by_id(message_id: id):
    """Создаёт запрос находящий сообщение по его id"""
    q = select()
    q = (
        q.add_columns(Message)
        .options(selectinload(Message.chat))
        .where(Message.id == message_id)
    )
    return q
