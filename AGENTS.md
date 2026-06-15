# Project Snapshot

- FastAPI backend for a portfolio chatbot API with LangGraph orchestration and OpenRouter LLM calls.
- Language/runtime: Python; `.python-version` says 3.13, Docker uses `python:3.12-slim` (`Needs verification`).
- Package manager: pip with pinned `requirements.txt`; no `pyproject.toml`, lockfile, Makefile, lint config, or test config found.
- Main entrypoint: `main.py` exposes `app`; Docker runs `uvicorn main:app --host 0.0.0.0 --port 8000`.
- Main source directories: `app/`, `knowledge/`, `scripts/`.
- Main runtime dependencies: FastAPI, LangGraph, OpenAI client against OpenRouter, SQLite, APScheduler, aiosmtplib, LangSmith.
- Tests: no `tests/` directory found.
- README setup mentions MongoDB and `docker-compose up -d`, but code/config use SQLite and no `docker-compose.yml` was found (`Needs verification`).

# Required Workflow

1. Read `AGENTS.md` first.
2. Use `Context Routing` to select only relevant `context/*.md` files.
3. Inspect related source before editing; context files are not a substitute for code.
4. Make the smallest coherent change.
5. Update tests when behavior changes; if no test harness exists, document the gap in the final response.
6. Update context files when structure, ownership, flows, dependencies, or responsibilities change.
7. Run the most relevant validation command available for the touched area.
8. Report what changed, what was validated, and whether context files changed.

# Context Routing

Task related to FastAPI startup, middleware, CORS, environment settings, Docker, health checks, or process lifecycle:
Read `context/RUNTIME_API.md` first.

Task related to `/chat`, streaming NDJSON, classification, retrieval, generation, LangGraph routing, OpenRouter, LangSmith, prompt injection, or conversation responses:
Read `context/CHAT_AGENT.md` first.

Task related to `knowledge/`, embeddings, vector search, prompt markdown, prompt cache, or seed scripts:
Read `context/KNOWLEDGE_AND_PROMPTS.md` first.

Task related to contact collection, SMTP email, contact templates, contact leads, translated confirmations, or email rate limits:
Read `context/CONTACT_FLOW.md` first.

Task related to SQLite schema, conversation history, JWT cookie usage, daily limits, soft delete, cleanup jobs, or DB initialization:
Read `context/PERSISTENCE_AND_LIMITS.md` first.

# Validation

- Install dependencies: `.venv/bin/pip install -r requirements.txt` if the venv is missing dependencies.
- Seed required prompts before running the app against a fresh SQLite DB: `.venv/bin/python -m scripts.seed_prompts`.
- Seed knowledge embeddings when `knowledge/*_knowledge/*.md` changes: `.venv/bin/python -m scripts.seed_knowledge` (requires `OPENROUTER_API_KEY`).
- Run dev server: `.venv/bin/uvicorn main:app --reload`.
- Health check after startup: `GET /health` should return `{"status":"ok"}`.
- There is no configured automated test, lint, format, or typecheck command in the repo.

# File Change Policy

- Do not edit `.env`, `data/*.db*`, `.langgraph_api/*`, `.venv/`, or `logs/`; treat them as local/generated state.
- If changing DB schema in `app/db/connection.py`, check seed scripts and services that write/read the affected tables.
- If changing graph state keys, update `app/agent/state.py` and every node/route that reads those keys.
- If changing prompt keys, update `scripts/seed_prompts.py` and all `get_prompt(...)` call sites together.

# Documentation Policy

- Keep `AGENTS.md` operational and concise; put module-specific behavior in `context/*.md`.
- Update the relevant context file when a change alters module responsibilities, runtime flow, dependencies, or setup commands.
- Do not preserve README claims that conflict with executable code unless marked `Needs verification`.

# Security Policy

- Never commit real `.env` values, API keys, SMTP credentials, LangSmith keys, or SQLite data files.
- Contact flow handles names, emails, messages, IPs, and traces; avoid adding logs/traces that expose more PII.
- `langsmith_tracer.py` anonymizes exact standalone IP/email-like strings only; do not assume arbitrary prompt contents are sanitized.

# Final Response Requirements

- State code/context files changed.
- State validation run, or why validation was not run.
- State whether any context files were created or updated.
