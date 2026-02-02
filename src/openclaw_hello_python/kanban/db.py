from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from openclaw_hello_python.kanban.models import Base


DEFAULT_DB_PATH = Path(os.environ.get("KANBAN_DB_PATH", "kanban.db"))


def build_sqlite_url(path: Path) -> str:
    return f"sqlite:///{path}"


def get_engine(db_url: str | None = None):
    url = db_url or build_sqlite_url(DEFAULT_DB_PATH)
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(url, connect_args=connect_args, future=True)


def init_db(engine) -> None:
    Base.metadata.create_all(engine)


def get_session_factory(engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
