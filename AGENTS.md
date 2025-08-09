# Repository Guidelines

## Project Structure & Module Organization
- Source: `src/` (Flask app in `app.py`, autocomplete in `autocomplete/`, search in `search/`, crawler in `web_crawler/`).
- Tests: `src/tests/` (pytest). Static assets: `src/static/`.
- Runtime data: `logs/` and `pickles/` (created by `make scaffold`; `pickles/` is git-ignored).
- Orchestration: `docker-compose.yml`; build config in `Dockerfile`; developer tasks in `Makefile`.

## Build, Test, and Development Commands
- `make install`: Install runtime and dev dependencies.
- `make build`: Build the Docker image `python:flask` and scaffold data dirs.
- `docker-compose up`: Start `server`, `redis`, and `log_reader` (app on `http://localhost:3000`).
- `make test`: Run pytest on `src/`.
- `make lint`: Run flake8 checks (errors then warnings).
- `make fix`: Format with Black.
- `make inverted_index`: Run the web crawler and POST a reload to the server (requires server running).

## Coding Style & Naming Conventions
- Python, 4-space indentation. Format with Black; lint with flake8 (line length 127, reasonable complexity).
- Modules/files and functions: `snake_case`; classes: `PascalCase`; constants: `UPPER_SNAKE_CASE`.
- Keep modules focused; place web assets in `src/static/` and tests in `src/tests/`.

## Testing Guidelines
- Framework: pytest. Place tests under `src/tests/` and name files `test_*.py` (e.g., `test_pickle_store.py`).
- Run all tests: `make test`. Filter: `pytest src/tests -k pickle_store -q`.
- Prefer small, fast unit tests for `autocomplete`, `search`, and persistence (`PickleStore`).

## Commit & Pull Request Guidelines
- Commits: short, imperative subject lines (e.g., "Add trie visualization", "Fix lint errors").
- Include scope when helpful (e.g., `search:`). Keep changes focused.
- PRs: clear description, rationale, test plan, and any screenshots of UI (`src/static/`). Link issues (e.g., `Closes #123`). Update README if commands or behavior change.

## Security & Configuration Tips
- Config lives in `src/env.py` (paths, `REDIS_URL`). Avoid hardcoding secrets; none are required to run.
- Do not commit generated artifacts (`pickles/`, `*.pkl`); logs are mounted—avoid committing large log files.
