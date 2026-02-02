# openclaw-hello-python

A tiny Python **3.11** “hello world” CLI project.

## Requirements

- Python **3.11+**

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e .
openclaw-hello-python
openclaw-hello-python --name Steve
```

## Run the Kanban webapp

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e .
uvicorn openclaw_hello_python.webapp:app --reload
```

Open `http://127.0.0.1:8000/` in a browser. The app stores data in `kanban.db` by default.
To override the database location, set `KANBAN_DB_URL` (example: `sqlite:////absolute/path/kanban.db`).

## Test

```bash
pip install -e .
pip install pytest
pytest -q
```
Hello world Python project (3.11) for OpenClaw demos
