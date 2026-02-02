from __future__ import annotations

import os
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openclaw_hello_python.kanban import (
    CardNotFoundError,
    Column,
    board_snapshot,
    create_card,
    delete_card,
    move_column,
    shift_card,
)
from openclaw_hello_python.kanban.db import get_engine, get_session_factory, init_db
from openclaw_hello_python.kanban.models import Card

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


def create_app() -> FastAPI:
    app = FastAPI()

    db_url = os.environ.get("KANBAN_DB_URL")
    engine = get_engine(db_url)
    init_db(engine)
    session_factory = get_session_factory(engine)

    templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

    def get_db() -> Session:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    def is_htmx(request: Request) -> bool:
        return request.headers.get("HX-Request") == "true"

    def render_board(request: Request, db: Session) -> HTMLResponse:
        board = board_snapshot(db)
        columns = list(Column)
        if is_htmx(request):
            return templates.TemplateResponse(
                "partials/board.html",
                {"request": request, "board": board, "columns": columns},
            )
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "board": board, "columns": columns},
        )

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request, db: Session = Depends(get_db)):
        return render_board(request, db)

    @app.post("/cards", response_class=HTMLResponse)
    def create(
        request: Request,
        title: str = Form(...),
        column: Column = Form(Column.TODO),
        db: Session = Depends(get_db),
    ):
        if not title.strip():
            raise HTTPException(status_code=400, detail="Title required")
        create_card(db, title.strip(), column)
        return render_board(request, db)

    @app.post("/cards/{card_id}/delete", response_class=HTMLResponse)
    def remove(request: Request, card_id: int, db: Session = Depends(get_db)):
        try:
            delete_card(db, card_id)
        except CardNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return render_board(request, db)

    @app.post("/cards/{card_id}/shift", response_class=HTMLResponse)
    def shift(
        request: Request,
        card_id: int,
        direction: str = Form(...),
        db: Session = Depends(get_db),
    ):
        try:
            shift_card(db, card_id, direction)
        except CardNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return render_board(request, db)

    @app.post("/cards/{card_id}/move", response_class=HTMLResponse)
    def move(
        request: Request,
        card_id: int,
        direction: str = Form(...),
        db: Session = Depends(get_db),
    ):
        try:
            move_column(db, card_id, direction)
        except CardNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return render_board(request, db)

    @app.post("/cards/{card_id}/edit", response_class=HTMLResponse)
    def edit(
        request: Request,
        card_id: int,
        title: str = Form(...),
        db: Session = Depends(get_db),
    ):
        title = title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="Title required")
        card = db.get(Card, card_id)
        if card is None:
            raise HTTPException(status_code=404, detail="Card not found")
        card.title = title
        db.commit()
        return render_board(request, db)

    return app


app = create_app()
