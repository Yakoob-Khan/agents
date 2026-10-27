# Lab 02 — Agent loop

A hand-written agent loop. Claude (Sonnet 5.5) gets three read-only tools (`list_files`, `read_file`, `grep`) over lab 01's source files and explores until it can answer a question. Every message added to the conversation is printed as JSON, with token usage and cost for each step. Design: [`DESIGN.md`](DESIGN.md).

- `main.py`: the loop. Sends the history, checks `stop_reason`, runs the requested tools, appends the results, repeats.
- `tools.py`: the tool definitions the model sees, and the functions the loop runs. Only `main.py`, `test_main.py`, `README.md` and `DESIGN.md` in `labs/01-messages/` are reachable.
- [`agent-loop.html`](agent-loop.html): a visual walkthrough of the loop, using the first real run. Open it in a browser (`open agent-loop.html`).

## Setup

Uses the repo-root `.env` from lab 01 (see [`../01-messages/README.md`](../01-messages/README.md)). From this folder:

```bash
uv sync
```

## Run

```bash
uv run --env-file ../../.env main.py
uv run --env-file ../../.env main.py "How does streaming work?"
```

With no argument it asks the design's question: "How is cost calculated in implementation and whether it is tested well?"

## Checks

```bash
uv run ruff check . && uv run ruff format --check .
uv run mypy .
uv run pytest -q
```
