from pydantic import BaseModel
from sqlalchemy import delete, insert, update
from sqlalchemy.dialects.postgresql import insert

from db import Base


def add_new_model(schema: BaseModel, model: Base):
    """Создаёт запрос на добавление новой модели"""
    q = insert(model).values(schema.model_dump())
    return q


def delete_model_by_id(id: int, model: Base):
    """Создаёт запрос на удаление модели по её id"""
    q = delete(model).where(model.id == id)
    return q


def update_model_q(model: Base, schema: BaseModel):
    """Создаёт запрос на обновление модели по её id"""
    q = update(model).where(model.id == schema.id).values(**schema.model_dump())
    return q
