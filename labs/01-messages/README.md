# Lab 01 — Messages

Send one prompt to Claude (Sonnet 5.5), print the answer, then the response metadata, approximate cost, and latency. Design: [`DESIGN.md`](DESIGN.md).

## One-time setup

1. Create an API key at [platform.claude.com](https://platform.claude.com) (Settings → API keys). API usage is billed there, separately from a Claude.ai subscription.
2. From the repo root, copy the example env file and paste your key into it:
   ```bash
   cp .env.example .env
   ```
   `.env` is git-ignored, so the key never gets committed. Don't paste the key into a chat or a tracked file.
3. Install dependencies (from this folder):
   ```bash
   uv sync
   ```

## Run

From this folder (`labs/01-messages`):

```bash
uv run --env-file ../../.env main.py "What is a context window?"
uv run --env-file ../../.env main.py --effort low "What is a context window?"
```

`--env-file` loads the key into the environment for that one run only.

## Checks

```bash
uv run ruff check . && uv run ruff format --check .
uv run mypy .
uv run pytest -q
```

## Retro

_After building: what surprised me, what I'd change._
