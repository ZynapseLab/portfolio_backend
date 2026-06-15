# Chat Agent Context

- `/chat` in `app/routes/chat.py` streams `application/x-ndjson`; emitted graph custom events are serialized as one JSON object per line.
- Chat flow checks daily rate limit before graph execution, creates/loads the active conversation for `(ip, scope, date)`, appends the user message, streams the graph, then appends the assistant response if tokens were produced.
- LangGraph entrypoint is `app/agent/graph.py:compiled_graph`; `langgraph.json` exposes it as `conversation_agent`.
- Graph order: `classify` routes to `retrieve -> generate`, `contact_handler`, or `reject`; `CONTACT_INCOMPLETE` is routed through retrieval then generation with contact collection instructions.
- Classifier can override `scope` from `global` to `jonathan` or `pablo`; preserve valid scopes `jonathan`, `pablo`, `global` unless updating knowledge seeding/search too.
- OpenRouter client is centralized in `app/agent/llm.py`; chat, classifier, translator, and embeddings use model names from settings except embeddings, which use `openai/text-embedding-3-small` directly.
- LangSmith callbacks are attached both on compiled graph creation and per request config; check tracing behavior before changing callback wiring.
