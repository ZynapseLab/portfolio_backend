"""
Seed Weaviate knowledge collections from markdown files in knowledge/.

Usage:
    python -m scripts.seed_knowledge

Each markdown file is split into semantic chunks by level-2 headers (## ...).
Every chunk gets its OWN embedding and object in Weaviate, which yields
much better precision during vector search than one embedding per file.

Embeddings are reused when the stored content hash and embedding model match
the current chunk. Only new or changed chunks call the embedding API.

The parent title (# ...) is prepended to each chunk so the embedding always
carries the broader topic context (e.g. "Professional Experience - Full History
> Vertebra" instead of just "Vertebra").
"""

import asyncio
import sys
from pathlib import Path

import joblib
from openai import AsyncOpenAI
from weaviate.collections.classes.data import DataObject
from weaviate.util import generate_uuid5

from app.config import settings
from app.services.knowledge.chunker import MarkdownChunker
from app.services.knowledge.vectorizer import OpenRouterVectorizer
from app.services.vector_store_service import weaviate_client_manager
from app.services.vector_store_service.schemas import KNOWLEDGE_COLLECTIONS

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"
VECTOR_CACHE_DIR = KNOWLEDGE_DIR / "vectors"
BATCH_SIZE = 20

# Folders with raw knowledge content (markdown files)
KNOWLEDGES = ["devs", "projects"]

# Maps knowledge collection names to their corresponding scope (e.g. "jonathan_knowledge" -> "jonathan")
SCOPE_MAP = {
    "jonathan_knowledge": "jonathan",
    "pablo_knowledge": "pablo",
}


def _cache_path(collection_name: str) -> Path:
    """
    Returns the path to the cache file for the given collection name.

    Args:
        collection_name (str): The name of the collection.

    Returns:
        Path: The path to the cache file.
    """
    return VECTOR_CACHE_DIR / f"{collection_name}.joblib"


def _load_vector_cache(collection_name: str) -> dict[str, dict]:
    """
    Loads the vector cache for the given collection name.

    Args:
        collection_name (str): The name of the collection.

    Returns:
        dict[str, dict]: The loaded cache entries, or an empty dictionary if the cache does not exist.
    """
    path = _cache_path(collection_name)

    if not path.exists():
        return {}

    cache = joblib.load(path)
    if not isinstance(cache, dict):
        return {}

    return cache.get("entries", {})


def _dump_vector_cache(collection_name: str, entries: dict[str, dict]) -> None:
    """
    Dumps the vector cache for the given collection name.

    Args:
        collection_name (str): The name of the collection.
        entries (dict[str, dict]): The cache entries to be dumped.
    """
    VECTOR_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        {
            "collection": collection_name,
            "embedding_model": settings.OPENROUTER_EMBEDDING_MODEL,
            "entries": entries,
        },
        _cache_path(collection_name),
    )


def _entry_matches(properties: dict, entry: dict) -> bool:
    """
    Checks if the given properties match the properties of the given entry.

    Args:
        properties (dict): The properties to check.
        entry (dict): The entry to compare against.

    Returns:
        bool: True if the properties match, False otherwise.
    """
    return (
        properties.get("content_hash") == entry["content_hash"]
        and properties.get("embedding_model") == entry["embedding_model"]
    )


def _extract_vector(vector) -> list[float] | None:
    """
    Extracts the vector from the given vector representation.

    Args:
        vector: The vector representation to extract from.

    Returns:
        list[float] | None: The extracted vector, or None if the vector could not be extracted.
    """
    if isinstance(vector, list):
        return vector

    if isinstance(vector, dict):
        default_vector = vector.get("default")
        if isinstance(default_vector, list):
            return default_vector

    return None


async def _upsert_vectors(
    collection, existing: dict[str, dict], vectors: list[tuple[dict, list[float]]]
) -> None:
    """
    Upserts the vectors into the collection, replacing existing entries if necessary.

    Args:
        collection: The collection to upsert vectors into.
        existing (dict[str, dict]): The existing entries in the collection.
        vectors (list[tuple[dict, list[float]]]): The vectors to upsert.
    """
    new_objects = []

    for entry, embedding in vectors:
        object_uuid = generate_uuid5(entry["source_id"])

        if entry["source_id"] in existing:
            await collection.data.replace(
                uuid=object_uuid,
                properties=entry,
                vector=embedding,
            )
        else:
            new_objects.append(
                DataObject(
                    uuid=object_uuid,
                    properties=entry,
                    vector=embedding,
                )
            )

    if new_objects:
        await collection.data.insert_many(new_objects)


async def _prepare_vector_cache(
    collection_name: str,
    entries: list[dict],
    vectorizer: OpenRouterVectorizer,
) -> dict[str, dict]:
    vector_cache = _load_vector_cache(collection_name)
    current_cache: dict[str, dict] = {}
    entries_to_embed = []

    for entry in entries:
        source_id = entry["source_id"]
        cached = vector_cache.get(source_id)
        cached_properties = cached.get("properties", {}) if cached else {}
        cached_vector = cached.get("vector") if cached else None

        if cached_vector and _entry_matches(cached_properties, entry):
            current_cache[source_id] = {
                "properties": entry,
                "vector": cached_vector,
            }
            continue

        entries_to_embed.append(entry)

    if entries_to_embed:
        print(
            f"\n{collection_name}: generating embeddings for "
            f"{len(entries_to_embed)} changed chunk(s) (batch size {BATCH_SIZE})..."
        )

        for i in range(0, len(entries_to_embed), BATCH_SIZE):
            batch = entries_to_embed[i : i + BATCH_SIZE]
            texts = [entry["embed_text"] for entry in batch]
            embeddings = await vectorizer.vectorize_many(texts)

            for entry, embedding in zip(batch, embeddings):
                current_cache[entry["source_id"]] = {
                    "properties": entry,
                    "vector": embedding,
                }

            print(f"  Batch {i // BATCH_SIZE + 1}: {len(batch)} embedding(s)")
    else:
        print(f"\n{collection_name}: reused all vectors from joblib cache.")

    _dump_vector_cache(collection_name, current_cache)
    return current_cache


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

    # Collect all chunks first, then embed only chunks missing or changed in Weaviate.
    entries_by_knowledge: dict[str, list[dict]] = {
        knowledge: [] for knowledge in KNOWLEDGES
    }

    for knowledge in KNOWLEDGES:
        for source in sorted((KNOWLEDGE_DIR / knowledge).iterdir()):
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
                entries_by_knowledge[knowledge].append(
                    {
                        "source_id": source_id,
                        "scope": scope,
                        "source_heading": chunk["source_heading"],
                        "section_heading": chunk["section_heading"],
                        "chunk_index": chunk["chunk_index"],
                        "section_text": chunk["section_text"],
                        "embed_text": chunk["embed_text"],
                        "content_hash": chunk["embed_hash"],
                        "embedding_model": settings.OPENROUTER_EMBEDDING_MODEL,
                    }
                )
            print(f"  {source.name}: {len(chunks)} chunk(s)")

    vector_caches: dict[str, dict[str, dict]] = {}
    for knowledge, entries in entries_by_knowledge.items():
        if not entries:
            print(f"\n{KNOWLEDGE_COLLECTIONS[knowledge]}: no chunks found. Skipping.")
            continue

        collection_name = KNOWLEDGE_COLLECTIONS[knowledge]
        vector_caches[collection_name] = await _prepare_vector_cache(
            collection_name,
            entries,
            vectorizer,
        )

    try:
        async with weaviate_client_manager as client:
            for knowledge, entries in entries_by_knowledge.items():
                if not entries:
                    continue

                collection_name = KNOWLEDGE_COLLECTIONS[knowledge]

                # Ensure the collection exists and load existing entries
                await weaviate_client_manager.ensure_collection(collection_name)
                collection = client.collections.get(collection_name)
                existing = await weaviate_client_manager.load_existing(collection)
                vector_cache = vector_caches[collection_name]
                vectors_to_upsert: list[tuple[dict, list[float]]] = []

                for entry in entries:
                    source_id = entry["source_id"]
                    cached = vector_cache.get(source_id)
                    cached_vector = cached.get("vector") if cached else None
                    existing_properties = existing.get(source_id, {})

                    if cached_vector and not _entry_matches(existing_properties, entry):
                        vectors_to_upsert.append((entry, cached_vector))

                if vectors_to_upsert:
                    await _upsert_vectors(collection, existing, vectors_to_upsert)
                    print(
                        f"\n{collection_name}: upserted {len(vectors_to_upsert)} "
                        "vector(s) into Weaviate from joblib cache."
                    )
                else:
                    print(
                        f"\n{collection_name}: Weaviate already has the current vectors."
                    )

                # Delete stale objects from the collection
                stale_source_ids = set(existing) - {
                    entry["source_id"] for entry in entries
                }

                for source_id in sorted(stale_source_ids):
                    await collection.data.delete_by_id(generate_uuid5(source_id))
                if stale_source_ids:
                    print(f"  Deleted {len(stale_source_ids)} stale chunk(s)")

                print(f"  Seeded {len(entries)} chunk(s) into {collection_name}.")
    except RuntimeError as e:
        sys.stdout.flush()
        raise SystemExit(
            "\nVector joblib caches are up to date, but Weaviate upload failed.\n"
            f"{e}\n"
            "Start Weaviate with the configured host/ports and run the seed again."
        ) from None


if __name__ == "__main__":
    asyncio.run(main())
