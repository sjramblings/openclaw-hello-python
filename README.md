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

## Test

```bash
pip install -e .
pip install pytest
pytest -q
```
Hello world Python project (3.11) for OpenClaw demos
