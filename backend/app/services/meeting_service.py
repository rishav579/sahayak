import os
from bson import ObjectId

from app.db.mongo import get_database
from app.services.ai_service import extract_action_items, transcribe_audio
from app.utils.date_utils import compute_action_status
from app.utils.helpers import serialize_document, utc_now


async def create_meeting_from_upload(user_id: str, title: str, file_path: str, file_name: str, base_url: str):
    db = get_database()
    transcript = await transcribe_audio(file_path)
    extracted_items = await extract_action_items(transcript)

    meeting_doc = {
        "user_id": user_id,
        "title": title,
        "audio_url": f"{base_url}/uploads/{os.path.basename(file_path)}",
        "transcript": transcript,
        "action_items": [],
        "created_at": utc_now(),
    }
    meeting_result = await db.meetings.insert_one(meeting_doc)
    meeting_id = meeting_result.inserted_id

    action_item_docs = []
    for item in extracted_items:
        status = compute_action_status(item.get("deadline"), item.get("status", "pending"))
        action_item_doc = {
            "meeting_id": str(meeting_id),
            "task": item.get("task", "Untitled task"),
            "assignee": item.get("assignee"),
            "deadline": item.get("deadline"),
            "status": status,
            "reminder_sent": item.get("reminder_sent", False),
            "created_at": utc_now(),
        }
        result = await db.action_items.insert_one(action_item_doc)
        action_item_doc["_id"] = result.inserted_id
        action_item_docs.append(action_item_doc)

    await db.meetings.update_one(
        {"_id": meeting_id},
        {"$set": {"action_items": [doc["_id"] for doc in action_item_docs]}},
    )

    meeting = await db.meetings.find_one({"_id": meeting_id})
    serialized_meeting = serialize_document(meeting)
    serialized_items = [serialize_document(doc) for doc in action_item_docs]
    serialized_meeting["action_items"] = serialized_items

    return {
        "meeting": serialized_meeting,
        "transcript": transcript,
        "action_items": serialized_items,
    }


async def get_meetings_for_user(user_id: str):
    db = get_database()
    meetings = await db.meetings.find({"user_id": user_id}).sort("created_at", -1).to_list(length=100)
    results = []
    for meeting in meetings:
        serialized = serialize_document(meeting)
        items = await db.action_items.find({"meeting_id": serialized["_id"]}).to_list(length=100)
        enriched_items = []
        for item in items:
            serialized_item = serialize_document(item)
            serialized_item["status"] = compute_action_status(serialized_item.get("deadline"), serialized_item.get("status", "pending"))
            enriched_items.append(serialized_item)
        serialized["action_items"] = enriched_items
        results.append(serialized)
    return results


async def get_meeting_by_id(meeting_id: str, user_id: str):
    db = get_database()
    meeting = await db.meetings.find_one({"_id": ObjectId(meeting_id), "user_id": user_id})
    if not meeting:
        return None
    serialized = serialize_document(meeting)
    items = await db.action_items.find({"meeting_id": meeting_id}).to_list(length=100)
    enriched_items = []
    for item in items:
        serialized_item = serialize_document(item)
        serialized_item["status"] = compute_action_status(serialized_item.get("deadline"), serialized_item.get("status", "pending"))
        enriched_items.append(serialized_item)
    serialized["action_items"] = enriched_items
    return serialized
