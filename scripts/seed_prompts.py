"""Seed script to populate the prompts table in SQLite."""

from pathlib import Path

from app.db.connection import init_db, get_connection, close_db

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "knowledge" / "system_prompts"
ERRORS_DIR = PROMPTS_DIR / "errors"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


PROMPTS = [
    {"key": "system_prompt", "content": _read(PROMPTS_DIR / "system_prompt.md")},
    {
        "key": "classifier_prompt",
        "content": _read(PROMPTS_DIR / "classifier_prompt.md"),
    },
    {
        "key": "contact_collect_prompt",
        "content": _read(PROMPTS_DIR / "contact_collect_prompt.md"),
    },
    {
        "key": "out_of_domain_response",
        "content": _read(ERRORS_DIR / "out_of_domain_response.md"),
    },
    {
        "key": "prompt_injection_response",
        "content": _read(ERRORS_DIR / "prompt_injection_response.md"),
    },
    {
        "key": "contact_confirmation",
        "content": _read(ERRORS_DIR / "contact_confirmation.md"),
    },
    {"key": "contact_error", "content": _read(ERRORS_DIR / "contact_error.md")},
    {
        "key": "contact_rate_limit",
        "content": _read(ERRORS_DIR / "contact_rate_limit.md"),
    },
]


def seed():
    init_db()
    conn = get_connection()

    for prompt in PROMPTS:
        conn.execute(
            "INSERT INTO prompts (key, content) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET content=excluded.content",
            (prompt["key"], prompt["content"]),
        )
        print(f"  Upserted prompt: {prompt['key']}")

    conn.commit()
    close_db()
    print(f"Seeded {len(PROMPTS)} prompts.")


if __name__ == "__main__":
    seed()
