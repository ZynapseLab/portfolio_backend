from bson import ObjectId

from app.db.collections import conversations_col


async def get_or_create_conversation(ip: str, scope: str, date: str) -> dict:
    col = conversations_col()
    doc = await col.find_one({"ip": ip, "scope": scope, "date": date, "deleted": False})

    if doc:
        return doc

    result = await col.insert_one({
        "ip": ip,
        "scope": scope,
        "date": date,
        "messages": [],
        "messages_used": 0,
        "deleted": False,
    })
    
    return await col.find_one({"_id": result.inserted_id})


async def append_message(conversation_id: ObjectId, role: str, content: str) -> None:
    col = conversations_col()
    await col.update_one(
        {"_id": conversation_id},
        {"$push": {"messages": {"role": role, "content": content}}},
    )


async def increment_messages_used(conversation_id: ObjectId) -> int:
    col = conversations_col()
    result = await col.find_one_and_update(
        {"_id": conversation_id},
        {"$inc": {"messages_used": 1}},
        return_document=True,
    )
    return result["messages_used"]


async def get_messages_used(ip: str, scope: str, date: str) -> int:
    col = conversations_col()
    pipeline = [
        {"$match": {"ip": ip, "scope": scope, "date": date}},
        {"$group": {"_id": None, "total": {"$sum": "$messages_used"}}},
    ]
    cursor = col.aggregate(pipeline)
    result = await cursor.to_list(length=1)
    if not result:
        return 0
    return result[0]["total"]


async def soft_delete_conversation(ip: str, scope: str, date: str) -> bool:
    col = conversations_col()
    result = await col.update_one(
        {"ip": ip, "scope": scope, "date": date, "deleted": False},
        {"$set": {"deleted": True}},
    )
    return result.modified_count > 0


async def get_active_messages(ip: str, scope: str, date: str) -> list[dict]:
    col = conversations_col()
    doc = await col.find_one(
        {"ip": ip, "scope": scope, "date": date, "deleted": False},
        {"messages": 1},
    )
    if not doc:
        return []
    return doc.get("messages", [])


async def daily_cleanup(before_date: str) -> int:
    col = conversations_col()
    result = await col.update_many(
        {"date": {"$lt": before_date}, "deleted": False},
        {"$set": {"deleted": True}},
    )
    return result.modified_count


async def ensure_indexes() -> None:
    col = conversations_col()
    await col.create_index([("ip", 1), ("scope", 1), ("date", 1)])

    from app.db.collections import contact_leads_col
    cl = contact_leads_col()
    await cl.create_index([("ip", 1), ("timestamp", 1)])
