# Agent Development Guide

- Setup: `uv sync`
- Run: `uv run script.py` (multithreaded downloader)
- Tests (all): `uv run test.py`
- Lint/format: none configured; optionally run `black .` and `isort .`
- Type checks: optional `mypy .` if installed; add hints to new code
- Imports: stdlib, third-party (`requests`, `bs4`, `pandas`, `wand`), then local
- Naming: snake_case for functions/vars; UPPER_CASE constants; CapWords classes
- Formatting: PEP 8; keep lines ≤ 100 chars; no one-letter names
- Errors: prefer graceful handling; use `log_error`, `log_info`, `debug_print`/`log_debug`
- Concurrency: use `ThreadPoolExecutor`; guard shared sets/files with locks
- Shared state: modify `done_players`, `skipped_players`, `downloaded_events` only under locks
- I/O: create directories atomically; avoid race conditions; respect `REQUEST_DELAY`
- Config: read tunables from `config.py`; avoid hardcoded magic numbers
- Tests pattern: network calls may fail; keep retries/backoff consistent with code
- Editor rules: No Cursor or Copilot rules detected in repo
- Output dir: `MinifaceServer/content/miniface-server/` (script `chdir`s there)
