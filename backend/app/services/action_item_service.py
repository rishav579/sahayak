from bson import ObjectId

from app.db.mongo import get_database
from app.utils.date_utils import compute_action_status
from app.utils.helpers import serialize_document


async def list_action_items(user_id: str, status: str | None = None):
    db = get_database()
    meetings = await db.meetings.find({"user_id": user_id}).to_list(length=1000)
    meeting_ids = [str(meeting["_id"]) for meeting in meetings]

    query = {"meeting_id": {"$in": meeting_ids}} if meeting_ids else {"meeting_id": {"$in": []}}
    items = await db.action_items.find(query).sort("created_at", -1).to_list(length=1000)

    serialized = []
    for item in items:
        doc = serialize_document(item)
        doc["status"] = compute_action_status(doc.get("deadline"), doc.get("status", "pending"))
        if not status or doc["status"] == status:
            serialized.append(doc)
    return serialized


async def mark_action_item_complete(action_item_id: str, user_id: str):
    db = get_database()
    item = await db.action_items.find_one({"_id": ObjectId(action_item_id)})
    if not item:
        return None
    meeting = await db.meetings.find_one({"_id": ObjectId(item["meeting_id"]), "user_id": user_id})
    if not meeting:
        return None
    await db.action_items.update_one({"_id": ObjectId(action_item_id)}, {"$set": {"status": "completed"}})
    updated = await db.action_items.find_one({"_id": ObjectId(action_item_id)})
    return serialize_document(updated)


async def send_mock_reminder(action_item_id: str, user_id: str):
    db = get_database()
    item = await db.action_items.find_one({"_id": ObjectId(action_item_id)})
    if not item:
        return None
    meeting = await db.meetings.find_one({"_id": ObjectId(item["meeting_id"]), "user_id": user_id})
    if not meeting:
        return None
    await db.action_items.update_one({"_id": ObjectId(action_item_id)}, {"$set": {"reminder_sent": True}})
    updated = await db.action_items.find_one({"_id": ObjectId(action_item_id)})
    return serialize_document(updated)
