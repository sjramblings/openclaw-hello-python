from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Column(StrEnum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"


COLUMN_ORDER: tuple[Column, ...] = (Column.TODO, Column.DOING, Column.DONE)


class Base(DeclarativeBase):
    pass


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    column: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, index=True)


@dataclass(frozen=True)
class BoardColumn:
    name: str
    cards: list[Card]
