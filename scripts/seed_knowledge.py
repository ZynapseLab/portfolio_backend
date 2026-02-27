"""
Seed the knowledge_base table from markdown files in knowledge/.

Usage:
    python -m scripts.seed_knowledge

Each markdown file is split into semantic chunks by level-2 headers (## ...).
Every chunk gets its OWN embedding and row in the database, which yields
much better precision during vector search than one embedding per file.

The parent title (# ...) is prepended to each chunk so the embedding always
carries the broader topic context (e.g. "Professional Experience - Full History
> Vertebra" instead of just "Vertebra").
"""

import asyncio
import json
import re
import sqlite3
from pathlib import Path

from openai import AsyncOpenAI

from app.config import settings

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"

SCOPE_MAP = {
    "jonathan_knowledge": "jonathan",
    "pablo_knowledge": "pablo",
    "project_knowledge": "project",
}

EMBEDDING_MODEL = "openai/text-embedding-3-small"
BATCH_SIZE = 20


def _extract_title(text: str) -> str | None:
    """Return the first level-1 header (# ...) or None."""
    match = re.search(r"^# (.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _split_by_sections(text: str) -> list[str]:
    """Split markdown into chunks delimited by ## headers.

    Each chunk contains the header and all content until the next header
    (or end of file).  If the file has no ## headers the whole text is
    returned as a single chunk.
    """
    parts = re.split(r"(?=^## )", text, flags=re.MULTILINE)
    chunks = [p.strip() for p in parts if p.strip()]
    return chunks


def _build_chunks(text: str) -> list[dict]:
    """Return a list of {slug, section_text, embed_text} dicts.

    Each chunk is a ## section.  The level-1 title is prepended to the
    text sent for embedding so the vector captures the broader context.
    """
    title = _extract_title(text)
    sections = _split_by_sections(text)

    chunks = []
    for i, section in enumerate(sections):
        header_match = re.match(r"^##\s+(.+)$", section, re.MULTILINE)
        slug = header_match.group(1).strip() if header_match else f"section_{i}"
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", slug).strip("_").lower()

        embed_text = f"{title}\n\n{section}" if title else section

        chunks.append(
            {
                "slug": slug,
                "section_text": section,
                "embed_text": embed_text,
            }
        )

    return chunks


async def _embed_batch(client: AsyncOpenAI, texts: list[str]) -> list[list[float]]:
    """Embed multiple texts in a single API call."""
    response = await client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


def _init_db() -> sqlite3.Connection:
    db_path = Path(settings.SQLITE_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute(
        """\
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT UNIQUE NOT NULL,
            scope     TEXT NOT NULL,
            sections  TEXT NOT NULL,
            embedding TEXT NOT NULL
        )"""
    )
    conn.commit()
    return conn


async def main() -> None:
    conn = _init_db()
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY,
    )

    # Collect all chunks first, then embed in batches.
    entries: list[dict] = []

    for folder in sorted(KNOWLEDGE_DIR.iterdir()):
        if not folder.is_dir():
            continue

        scope = SCOPE_MAP.get(folder.name)
        if scope is None:
            print(f"  Skipping unknown folder: {folder.name}")
            continue

        md_files = sorted(folder.glob("*.md"))
        print(f"\n[{scope}] Found {len(md_files)} file(s)")

        for md_file in md_files:
            text = md_file.read_text(encoding="utf-8")
            chunks = _build_chunks(text)

            if not chunks:
                print(f"  Skipping empty file: {md_file.name}")
                continue

            for chunk in chunks:
                source_id = f"{scope}/{md_file.stem}/{chunk['slug']}"
                entries.append(
                    {
                        "source_id": source_id,
                        "scope": scope,
                        "section_text": chunk["section_text"],
                        "embed_text": chunk["embed_text"],
                    }
                )
            print(f"  {md_file.name}: {len(chunks)} chunk(s)")

    # Embed in batches.
    print(f"\nGenerating embeddings for {len(entries)} chunks (batch size {BATCH_SIZE})...")
    all_embeddings: list[list[float]] = []

    for i in range(0, len(entries), BATCH_SIZE):
        batch = entries[i : i + BATCH_SIZE]
        texts = [e["embed_text"] for e in batch]
        embeddings = await _embed_batch(client, texts)
        all_embeddings.extend(embeddings)
        print(f"  Batch {i // BATCH_SIZE + 1}: {len(batch)} embeddings")

    # Upsert into DB.
    inserted = 0
    updated = 0

    for entry, embedding in zip(entries, all_embeddings):
        sections_json = json.dumps([entry["section_text"]], ensure_ascii=False)
        embedding_json = json.dumps(embedding)

        existing = conn.execute(
            "SELECT id FROM knowledge_base WHERE source_id = ?",
            (entry["source_id"],),
        ).fetchone()

        if existing:
            conn.execute(
                "UPDATE knowledge_base SET scope=?, sections=?, embedding=? WHERE source_id=?",
                (entry["scope"], sections_json, embedding_json, entry["source_id"]),
            )
            updated += 1
        else:
            conn.execute(
                "INSERT INTO knowledge_base (source_id, scope, sections, embedding) VALUES (?, ?, ?, ?)",
                (entry["source_id"], entry["scope"], sections_json, embedding_json),
            )
            inserted += 1

    conn.commit()
    conn.close()

    print(f"\nDone — inserted: {inserted}, updated: {updated}, total: {inserted + updated}")


if __name__ == "__main__":
    asyncio.run(main())
