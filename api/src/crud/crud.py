from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db import Base
from dependencies import Pagination, add_id_to_header, get_session
from querys import delete_model_by_id, update_model_q


async def get_models(
    db: Annotated[AsyncSession, Depends(get_session)],
    pg: Annotated[Pagination, Depends(Pagination)],
    count: str,
    q: Annotated[str, Query(default="*")],
):
    """Находит нужные модели в базе данных"""
    _count = await db.execute(count)
    _exe = await db.execute(q.offset(pg.offset).limit(pg.limit))
    return {
        "pages": {**pg.dict, "count": _count.scalar()},
        "cards": _exe.scalars().all(),
    }


async def get_model(
    db: Annotated[AsyncSession, Depends(get_session)],
    q: Annotated[str, Query(default="*")],
):
    """Находит нужную модель в базе данных"""
    card = await db.execute(q)
    card = card.scalar()
    if card:
        return card
    else:
        return None


async def add_model(
    db: Annotated[AsyncSession, Depends(get_session)],
    schema: Annotated[Base, Query(response_model=Base)],
    model: Base,
):
    """Создаёт новую модель в базе данных"""
    schema = schema.__dict__
    schema = model(**schema)
    db.add(schema)
    await db.commit()
    return schema.id


async def delete_model(
    db: Annotated[AsyncSession, Depends(get_session)],
    id: Annotated[int, Depends(add_id_to_header)],
    model: Base,
):
    """Удаляет модель из базы данных"""
    q = delete_model_by_id(id=id, model=model)
    await db.execute(q)
    await db.commit()
    return f"Запись успешно удалена!"


async def update_model(
    db: Annotated[AsyncSession, Depends(get_session)],
    model: Base,
    schema: Annotated[Base, Query(response_model=Base)],
):
    """Обновляет модель в базе данных"""
    q = update_model_q(model=model, schema=schema)
    await db.execute(q)
    await db.commit()
    return schema
