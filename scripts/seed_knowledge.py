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
from pathlib import Path

from openai import AsyncOpenAI

from app.config import settings
from app.services.knowledge import chunker
from app.services.knowledge.chunker import MarkdownChunker
from app.services.knowledge.vectorizer import OpenRouterVectorizer

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"
BATCH_SIZE = 20
KNOWLEDGES = ["devs", "projects"]
SCOPE_MAP = {
    "jonathan_knowledge": "jonathan",
    "pablo_knowledge": "pablo",
}


async def main() -> None:
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY,
    )

    vectorizer = OpenRouterVectorizer(
        client=client,
        model_name=settings.OPENROUTER_EMBEDDING_MODEL,
    )

    chunker = MarkdownChunker()

    # Collect all chunks first, then embed in batches.
    entries: list[dict] = []

    for _scope in KNOWLEDGES:
        for source in sorted((KNOWLEDGE_DIR / _scope).iterdir()):
            source_key = source.stem if source.is_file() else source.name
            scope = SCOPE_MAP.get(source_key)
            if scope is None:
                print(f"  Skipping unknown knowledge source: {source.name}")
                continue

            text = source.read_text(encoding="utf-8")
            chunks = chunker.build_chunks(text)

            if not chunks:
                print(f"  Skipping empty file: {source.name}")
                continue

            for chunk in chunks:
                source_id = f"{scope}/{chunk['slug']}"
                entries.append(
                    {
                        "source_id": source_id,
                        "scope": scope,
                        "source_heading": chunk["source_heading"],
                        "section_heading": chunk["section_heading"],
                        "chunk_index": chunk["chunk_index"],
                        "section_text": chunk["section_text"],
                        "embed_text": chunk["embed_text"],
                    }
                )
            print(f"  {source.name}: {len(chunks)} chunk(s)")

        print(json.dumps(entries[0], indent=2))

        # Embed in batches.
        # print(
        #     f"\nGenerating embeddings for {len(entries)} chunks (batch size {BATCH_SIZE})..."
        # )
        # all_embeddings: list[list[float]] = []

        # for i in range(0, len(entries), BATCH_SIZE):
        #     batch = entries[i : i + BATCH_SIZE]
        #     texts = [e["embed_text"] for e in batch]
        #     embeddings = await vectorizer.vectorize_many(texts)
        #     all_embeddings.extend(embeddings)
        #     print(f"  Batch {i // BATCH_SIZE + 1}: {len(batch)} embeddings")

        # Clean stale entries not present in current knowledge files.
        # valid_ids = {e["source_id"] for e in entries}
        # existing_ids = {
        #     row[0]
        #     for row in conn.execute("SELECT source_id FROM knowledge_base").fetchall()
        # }
        # stale_ids = existing_ids - valid_ids
        # if stale_ids:
        #     conn.executemany(
        #         "DELETE FROM knowledge_base WHERE source_id = ?",
        #         [(sid,) for sid in stale_ids],
        #     )
        #     print(f"\nCleaned {len(stale_ids)} stale chunk(s)")

    # # Upsert into DB.
    # inserted = 0
    # updated = 0

    # for entry, embedding in zip(entries, all_embeddings):
    #     sections_json = json.dumps([entry["section_text"]], ensure_ascii=False)
    #     embedding_json = json.dumps(embedding)

    #     existing = conn.execute(
    #         "SELECT id FROM knowledge_base WHERE source_id = ?",
    #         (entry["source_id"],),
    #     ).fetchone()

    #     if existing:
    #         conn.execute(
    #             "UPDATE knowledge_base SET scope=?, sections=?, embedding=? WHERE source_id=?",
    #             (entry["scope"], sections_json, embedding_json, entry["source_id"]),
    #         )
    #         updated += 1
    #     else:
    #         conn.execute(
    #             "INSERT INTO knowledge_base (source_id, scope, sections, embedding) VALUES (?, ?, ?, ?)",
    #             (entry["source_id"], entry["scope"], sections_json, embedding_json),
    #         )
    #         inserted += 1

    # conn.commit()
    # conn.close()

    # print(
    #     f"\nDone — inserted: {inserted}, updated: {updated}, total: {inserted + updated}"
    # )


if __name__ == "__main__":
    asyncio.run(main())
