# Knowledge And Prompts Context

- Prompt content lives under `knowledge/system_prompts/`; `scripts/seed_prompts.py` upserts fixed prompt keys into SQLite, and `app/services/prompt_service.py` only serves prompts loaded into its in-memory cache at startup.
- Adding/removing prompt keys requires coordinated changes in markdown files, `scripts/seed_prompts.py`, and every `get_prompt("...")` call site.
- Knowledge markdown is seeded from `knowledge/jonathan_knowledge`, `knowledge/pablo_knowledge`, and `knowledge/project_knowledge`; `SCOPE_MAP` in `scripts/seed_knowledge.py` maps those folders to DB scopes.
- `seed_knowledge` splits markdown by `##` sections, prepends the `#` title to embedding text, embeds batches with OpenRouter `openai/text-embedding-3-small`, deletes stale chunks, and upserts `knowledge_base` rows.
- Runtime retrieval loads all `knowledge_base` rows into `_knowledge_cache`; `global` scope searches only `jonathan` and `pablo`, not `project`.
- If knowledge files change, reseed with `.venv/bin/python -m scripts.seed_knowledge`; this requires `OPENROUTER_API_KEY` and can call the external API.
