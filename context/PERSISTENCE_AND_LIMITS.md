# Persistence And Limits Context

- Persistence is SQLite through a single module-level connection in `app/db/connection.py`; schema is created with `CREATE TABLE IF NOT EXISTS` during `init_db()`.
- DB path defaults to `./data/portfolio.db` via `SQLITE_DB_PATH`; `data/*.db*` files are local runtime state and should not be edited manually.
- Tables: `conversations`, `messages`, `prompts`, `knowledge_base`, and `contact_leads`.
- Conversation identity for active chat is `(ip, scope, UTC date, deleted=0)`; deletion is soft delete by setting `deleted=1`.
- Chat usage limit counts `SUM(messages_used)` for `(ip, scope, date)` across conversations, including soft-deleted conversations.
- `DELETE /conversation` uses JWT cookie scope when present, otherwise defaults to `global`, then writes a fresh JWT cookie.
- Daily cleanup job runs at 00:05 UTC and soft-deletes conversations before the current UTC date; it does not remove messages or contact leads.
