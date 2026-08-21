from app.db.mongo import get_database


async def ensure_indexes():
    db = get_database()
    await db.users.create_index("google_id", unique=True, name="uq_users_google_id")
    await db.users.create_index("email", unique=True, sparse=True, name="uq_users_email")
    await db.meetings.create_index([("user_id", 1), ("created_at", -1)], name="idx_meetings_user_created")
    await db.meetings.create_index([("user_id", 1), ("audio_filename", 1)], name="idx_meetings_user_media")
    await db.action_items.create_index([("meeting_id", 1), ("created_at", -1)], name="idx_action_items_meeting_created")
    await db.action_items.create_index([("status", 1), ("created_at", -1)], name="idx_action_items_status_created")
