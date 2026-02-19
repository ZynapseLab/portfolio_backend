"""Seed script to populate the knowledge_base collection with embeddings."""

import asyncio

from motor.motor_asyncio import AsyncIOMotorClient
from openai import AsyncOpenAI

from app.config import settings

KNOWLEDGE_ENTRIES = [
    {
        "source_id": "jonathan-skills",
        "scope": "jonathan",
        "sections": [
            "Jonathan is a full-stack developer specializing in modern web technologies.",
            "His core skills include TypeScript, React, Next.js, Node.js, Python, and FastAPI.",
            "He has experience with cloud platforms like AWS and GCP.",
            "Jonathan is passionate about building performant and accessible web applications.",
        ],
    },
    {
        "source_id": "pablo-skills",
        "scope": "pablo",
        "sections": [
            "Pablo is a software engineer with expertise in backend systems and AI/ML.",
            "His core skills include Python, FastAPI, LangChain, PostgreSQL, and MongoDB.",
            "He specializes in building intelligent systems and data pipelines.",
            "Pablo has experience deploying ML models in production environments.",
        ],
    },
    {
        "source_id": "joint-projects",
        "scope": "jonathan",
        "sections": [
            "Jonathan and Pablo collaborate on AI-powered web applications.",
            "Their portfolio includes chatbot systems, RAG applications, and full-stack projects.",
            "They focus on delivering high-quality, production-ready solutions.",
            "Their joint work combines frontend excellence with backend intelligence.",
        ],
    },
    {
        "source_id": "joint-projects-pablo",
        "scope": "pablo",
        "sections": [
            "Jonathan and Pablo collaborate on AI-powered web applications.",
            "Their portfolio includes chatbot systems, RAG applications, and full-stack projects.",
            "They focus on delivering high-quality, production-ready solutions.",
            "Their joint work combines frontend excellence with backend intelligence.",
        ],
    },
    {
        "source_id": "services",
        "scope": "jonathan",
        "sections": [
            "We offer custom web development services tailored to your needs.",
            "Our services include full-stack development, AI integration, and consulting.",
            "We build modern, scalable applications using cutting-edge technologies.",
            "Contact us for project inquiries and collaboration opportunities.",
        ],
    },
    {
        "source_id": "services-pablo",
        "scope": "pablo",
        "sections": [
            "We offer custom web development services tailored to your needs.",
            "Our services include full-stack development, AI integration, and consulting.",
            "We build modern, scalable applications using cutting-edge technologies.",
            "Contact us for project inquiries and collaboration opportunities.",
        ],
    },
]


async def generate_embedding(client: AsyncOpenAI, text: str) -> list[float]:
    response = await client.embeddings.create(
        model="openai/text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


async def seed():
    mongo_client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = mongo_client[settings.MONGODB_DATABASE]
    col = db["knowledge_base"]

    openai_client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY,
    )

    for entry in KNOWLEDGE_ENTRIES:
        combined_text = " ".join(entry["sections"])
        print(f"  Generating embedding for: {entry['source_id']}...")
        embedding = await generate_embedding(openai_client, combined_text)

        await col.update_one(
            {"source_id": entry["source_id"]},
            {
                "$set": {
                    "source_id": entry["source_id"],
                    "scope": entry["scope"],
                    "sections": entry["sections"],
                    "embedding": embedding,
                }
            },
            upsert=True,
        )
        print(f"  Upserted: {entry['source_id']}")

    print(f"Seeded {len(KNOWLEDGE_ENTRIES)} knowledge entries.")
    await openai_client.close()
    mongo_client.close()


if __name__ == "__main__":
    asyncio.run(seed())
