from __future__ import annotations

from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from openclaw_hello_python.kanban.models import COLUMN_ORDER, Card, Column


class CardNotFoundError(RuntimeError):
    pass


def list_cards(session: Session, column: Column) -> list[Card]:
    stmt = select(Card).where(Card.column == column.value).order_by(asc(Card.position), asc(Card.id))
    return list(session.scalars(stmt))


def _set_positions(cards: list[Card]) -> None:
    for idx, card in enumerate(cards):
        card.position = idx


def create_card(session: Session, title: str, column: Column) -> Card:
    card = Card(title=title, column=column.value, position=0)
    session.add(card)
    session.flush()

    cards = [c for c in list_cards(session, column) if c.id != card.id]
    cards.append(card)
    _set_positions(cards)
    session.commit()
    return card


def get_card(session: Session, card_id: int) -> Card:
    card = session.get(Card, card_id)
    if card is None:
        raise CardNotFoundError(f"Card {card_id} not found")
    return card


def delete_card(session: Session, card_id: int) -> None:
    card = get_card(session, card_id)
    column = Column(card.column)
    session.delete(card)
    session.flush()

    cards = list_cards(session, column)
    _set_positions(cards)
    session.commit()


def move_card(session: Session, card_id: int, new_column: Column, new_position: int | None = None) -> None:
    card = get_card(session, card_id)
    old_column = Column(card.column)

    old_cards = [c for c in list_cards(session, old_column) if c.id != card.id]
    _set_positions(old_cards)

    if new_position is None:
        new_position = len(list_cards(session, new_column))

    new_cards = list_cards(session, new_column)
    if new_column == old_column:
        new_cards = [c for c in new_cards if c.id != card.id]

    insert_at = max(0, min(new_position, len(new_cards)))
    new_cards.insert(insert_at, card)

    card.column = new_column.value
    _set_positions(new_cards)

    session.flush()
    session.commit()


def shift_card(session: Session, card_id: int, direction: str) -> None:
    card = get_card(session, card_id)
    column = Column(card.column)
    cards = list_cards(session, column)
    indices = {c.id: idx for idx, c in enumerate(cards)}
    current = indices.get(card.id, card.position)

    if direction == "up":
        new_position = max(0, current - 1)
    elif direction == "down":
        new_position = min(len(cards) - 1, current + 1)
    else:
        raise ValueError("direction must be 'up' or 'down'")

    move_card(session, card_id, column, new_position)


def move_column(session: Session, card_id: int, direction: str) -> None:
    card = get_card(session, card_id)
    current = Column(card.column)
    order = list(COLUMN_ORDER)
    index = order.index(current)

    if direction == "left" and index > 0:
        move_card(session, card_id, order[index - 1])
    elif direction == "right" and index < len(order) - 1:
        move_card(session, card_id, order[index + 1])


def board_snapshot(session: Session) -> dict[Column, list[Card]]:
    return {column: list_cards(session, column) for column in COLUMN_ORDER}
