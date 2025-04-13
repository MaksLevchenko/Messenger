from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, relationship, mapped_column, declared_attr

from db import Base

if TYPE_CHECKING:
    from models import Game


class CreatedAtMixin:
    """
    Миксин, добавляющий поле `created_at`, содержащее
    дату создания объекта (и обновляющее своё значение
    только один раз при создании объекта)
    """

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Дата создания",
    )


class UpdatedAtMixin:
    """
    Миксин, который добавляет поле `updated_at`, содержащее
    дату последнего изменения объекта, автоматически обновляющуюся
    при каждом изменении объекта
    """

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Дата обновления",
    )


class GameRelationMixin:
    """
    Миксин для сущности "Игра", содержащий поля game_id, game.
    """

    _game_back_populates: str | None = None

    @declared_attr
    def game_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey("games.id", ondelete="CASCADE"),
        )

    @declared_attr
    def game(cls) -> Mapped["Game"]:
        return relationship(argument="Game", back_populates=cls._game_back_populates)
