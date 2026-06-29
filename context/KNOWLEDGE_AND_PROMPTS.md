# Knowledge And Prompts Context

- Prompt content lives under `knowledge/system_prompts/`; `scripts/seed_prompts.py` upserts fixed prompt keys into SQLite, and `app/services/prompt_service.py` only serves prompts loaded into its in-memory cache at startup.
- Adding/removing prompt keys requires coordinated changes in markdown files, `scripts/seed_prompts.py`, and every `get_prompt("...")` call site.
- Knowledge markdown is seeded from mapped files under `knowledge/devs/` and `knowledge/projects/`; `SCOPE_MAP` in `scripts/seed_knowledge.py` maps source names to retrieval scopes.
- `seed_knowledge` splits markdown by `##` sections, prepends the `#` title to embedding text, and stores objects in Weaviate collections from `KNOWLEDGE_COLLECTIONS` with self-provided OpenRouter embeddings.
- Seeded Weaviate objects include `source_id`, chunk metadata, `content_hash`, and `embedding_model`; the seed script writes one `knowledge/vectors/<CollectionName>.joblib` vector cache per collection, reuses matching cached vectors before calling OpenRouter, then deletes stale Weaviate objects and stale cache entries.
- Runtime retrieval queries Weaviate `DevsKnowledge` with `near_vector`; `global` scope searches all dev entries and specific scopes filter by the `scope` property.
- If knowledge files change, reseed with `.venv/bin/python -m scripts.seed_knowledge`; this requires `OPENROUTER_API_KEY`, `WEAVIATE_URL`, `WEAVIATE_API_KEY`, and a reachable Weaviate Cloud cluster.
