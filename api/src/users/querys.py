from sqlalchemy import select, func
from sqlalchemy.orm import selectinload


from db.models import User


def select_user_by_id(id: int):
    """Создаёт запрос находящий пользователя по его id"""

    q = select()
    q = q.add_columns(User).options(selectinload(User.messages)).where(User.id == id)
    return q


def select_users_cards(user_id: int):
    """Создаёт запрос находящий всех пользователей"""

    q = select()

    count = q.add_columns(func.count(User.id).label("count"))
    q = (
        q.add_columns(User)
        .options(selectinload(User.messages))
        .where(User.id != user_id)
    )

    q = q.order_by(User.id)
    return count, q


def get_user_by_email(email: str):
    """Создаёт запрос находящий пользователя по его email"""
    q = select()
    q = q.add_columns(User).where(User.email == email)
    return q
