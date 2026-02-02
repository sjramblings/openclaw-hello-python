# Simple Kanban Web App Plan (Python 3.11)

Goal: a tiny, deployable kanban board for demos.

## Scope (MVP)

### Core UX

- Single page board: **To Do / Doing / Done**
- Cards have:
  - title (required)
  - description (optional)
  - created_at / updated_at
  - column + position
- Actions:
  - create card
  - edit card
  - delete card
  - move card between columns
  - reorder within a column

### Non-goals (MVP)

- Multi-board
- Real-time multi-user sync
- Attachments
- Complex permissions

## Tech choices (recommended defaults)

- Backend: **FastAPI**
- Templating: **Jinja2** (server-rendered HTML)
- Interactivity: **HTMX** (small, no SPA build)
- DB: **SQLite** (local/dev), via **SQLAlchemy**
- Styling: minimal CSS (optional: Tailwind CDN)
- Tests: `pytest`

Rationale: keeps it Python-only, minimal tooling, easy to run locally.

## Architecture

### Pages

- `GET /` → board page

### HTML partial endpoints (HTMX)

- `POST /cards` → create card (returns updated column HTML)
- `GET /cards/{id}/edit` → edit form partial
- `POST /cards/{id}` → update card (returns updated card HTML)
- `POST /cards/{id}/delete` → delete card (returns updated column HTML)
- `POST /cards/{id}/move` → move card to column + position (returns updated columns)

### JSON endpoints (optional)

Keep optional; prefer HTML partials for MVP.

## Data model

### Tables

`cards`
- `id` INTEGER PK
- `title` TEXT NOT NULL
- `description` TEXT NULL
- `column` TEXT NOT NULL  # todo|doing|done
- `position` INTEGER NOT NULL
- `created_at` DATETIME
- `updated_at` DATETIME

### Ordering rule

- `position` is contiguous per column (0..n-1)
- On move/reorder, renormalize positions for affected columns.

## Repo changes to implement

### Dependencies

Add to `pyproject.toml`:
- `fastapi`
- `uvicorn[standard]`
- `jinja2`
- `python-multipart` (for form posts)
- `sqlalchemy`

### New package layout

- `src/openclaw_hello_python/webapp/`
  - `app.py` (FastAPI app)
  - `db.py` (engine/session)
  - `models.py` (Card model)
  - `crud.py` (helpers)
  - `templates/`
    - `base.html`
    - `board.html`
    - `_column.html`
    - `_card.html`
    - `_edit_form.html`
  - `static/` (optional)

### Entrypoints

- Keep existing CLI (`openclaw-hello-python`) as-is.
- Add a new script:
  - `openclaw-hello-kanban = openclaw_hello_python.webapp.app:run`
  - Or document: `uvicorn openclaw_hello_python.webapp.app:app --reload`

## Acceptance criteria

- `uvicorn ...` starts successfully
- Visiting `/` shows 3 columns
- You can create/edit/delete cards
- Moving card changes column and preserves ordering
- Basic tests for CRUD + position normalization

## Nice-to-haves (post-MVP)

- Simple auth (single password)
- Multiple boards
- Search/filter
- Export/import JSON
- Dockerfile + fly.io / ECS deploy guide
