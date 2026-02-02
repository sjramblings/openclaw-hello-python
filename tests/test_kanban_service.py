from __future__ import annotations

from pathlib import Path

import pytest

from openclaw_hello_python.kanban import Column
from openclaw_hello_python.kanban.db import get_engine, get_session_factory, init_db
from openclaw_hello_python.kanban.service import (
    create_card,
    delete_card,
    list_cards,
    move_card,
    move_column,
    shift_card,
)


def make_session(tmp_path: Path):
    db_path = tmp_path / "kanban.db"
    engine = get_engine(f"sqlite:///{db_path}")
    init_db(engine)
    SessionLocal = get_session_factory(engine)
    return SessionLocal()


def test_create_and_delete_normalizes_positions(tmp_path: Path):
    session = make_session(tmp_path)
    try:
        card_a = create_card(session, "A", Column.TODO)
        card_b = create_card(session, "B", Column.TODO)

        cards = list_cards(session, Column.TODO)
        assert [c.id for c in cards] == [card_a.id, card_b.id]
        assert [c.position for c in cards] == [0, 1]

        delete_card(session, card_a.id)
        cards = list_cards(session, Column.TODO)
        assert [c.id for c in cards] == [card_b.id]
        assert [c.position for c in cards] == [0]
    finally:
        session.close()


def test_move_within_column_updates_order(tmp_path: Path):
    session = make_session(tmp_path)
    try:
        card_a = create_card(session, "A", Column.TODO)
        card_b = create_card(session, "B", Column.TODO)
        card_c = create_card(session, "C", Column.TODO)

        move_card(session, card_c.id, Column.TODO, 0)
        cards = list_cards(session, Column.TODO)
        assert [c.id for c in cards] == [card_c.id, card_a.id, card_b.id]
        assert [c.position for c in cards] == [0, 1, 2]
    finally:
        session.close()


def test_move_between_columns_normalizes(tmp_path: Path):
    session = make_session(tmp_path)
    try:
        card_a = create_card(session, "A", Column.TODO)
        card_b = create_card(session, "B", Column.TODO)
        create_card(session, "C", Column.DOING)

        move_card(session, card_b.id, Column.DOING, 0)
        todo_cards = list_cards(session, Column.TODO)
        doing_cards = list_cards(session, Column.DOING)

        assert [c.id for c in todo_cards] == [card_a.id]
        assert [c.position for c in todo_cards] == [0]
        assert [c.id for c in doing_cards][0] == card_b.id
        assert [c.position for c in doing_cards] == list(range(len(doing_cards)))
    finally:
        session.close()


def test_shift_and_column_move_helpers(tmp_path: Path):
    session = make_session(tmp_path)
    try:
        card_a = create_card(session, "A", Column.TODO)
        card_b = create_card(session, "B", Column.TODO)

        shift_card(session, card_b.id, "up")
        cards = list_cards(session, Column.TODO)
        assert [c.id for c in cards] == [card_b.id, card_a.id]

        move_column(session, card_b.id, "right")
        todo_cards = list_cards(session, Column.TODO)
        doing_cards = list_cards(session, Column.DOING)
        assert [c.id for c in todo_cards] == [card_a.id]
        assert [c.id for c in doing_cards] == [card_b.id]
    finally:
        session.close()
