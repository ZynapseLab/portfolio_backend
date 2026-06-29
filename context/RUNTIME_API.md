# Runtime API Context

- `main.py` creates the FastAPI app, validates required settings, initializes SQLite, loads prompts and knowledge cache, configures LangSmith env, starts APScheduler, and includes `health`, `chat`, and `conversation` routers.
- Required startup settings are enforced by `Settings.validate_required()`: `JWT_SECRET` cannot be `change-me`, and `OPENROUTER_API_KEY` must be set.
- Settings load from `.env` via `pydantic-settings`; `.env.example` is the safe reference for variable names.
- CORS defaults to `http://localhost:4321` and exposes chat usage headers: `X-Messages-Used`, `X-Messages-Limit`, `X-Reset-At`.
- Docker runs `uvicorn main:app --host 0.0.0.0 --port 8000`; README uses `.venv/bin/uvicorn main:app --reload` for local dev.
- `/health` executes `SELECT 1` through the initialized SQLite connection, so it fails if startup DB initialization failed.
- Weaviate is configured for Weaviate Cloud through `WEAVIATE_URL` and `WEAVIATE_API_KEY`; do not use local host/port settings for cloud deployments.
