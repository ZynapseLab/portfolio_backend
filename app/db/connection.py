import sqlite3
from pathlib import Path

from app.config import settings

_connection: sqlite3.Connection | None = None

_SCHEMA = """\
CREATE TABLE IF NOT EXISTS conversations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ip          TEXT    NOT NULL,
    scope       TEXT    NOT NULL,
    date        TEXT    NOT NULL,
    messages_used INTEGER NOT NULL DEFAULT 0,
    deleted     INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_conv_ip_scope_date
    ON conversations(ip, scope, date);

CREATE TABLE IF NOT EXISTS messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    role            TEXT    NOT NULL,
    content         TEXT    NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

CREATE TABLE IF NOT EXISTS prompts (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    key     TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS knowledge_base (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT UNIQUE NOT NULL,
    scope     TEXT NOT NULL,
    sections  TEXT NOT NULL,
    embedding TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS contact_leads (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT NOT NULL,
    email     TEXT NOT NULL,
    country   TEXT NOT NULL,
    subject   TEXT NOT NULL,
    message   TEXT NOT NULL,
    ip        TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_leads_ip_ts
    ON contact_leads(ip, timestamp);
"""


def init_db() -> None:
    global _connection
    db_path = Path(settings.SQLITE_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    _connection = sqlite3.connect(str(db_path), check_same_thread=False)
    _connection.row_factory = sqlite3.Row
    _connection.execute("PRAGMA journal_mode=WAL")
    _connection.execute("PRAGMA foreign_keys=ON")
    _connection.executescript(_SCHEMA)


def close_db() -> None:
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None


def get_connection() -> sqlite3.Connection:
    if _connection is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _connection
