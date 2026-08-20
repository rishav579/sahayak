from datetime import datetime, timezone
from typing import Any

from bson import ObjectId


def serialize_document(document: dict[str, Any] | None):
    if not document:
        return None
    serialized = {}
    for key, value in document.items():
        if isinstance(value, ObjectId):
            serialized[key] = str(value)
        elif isinstance(value, list):
            serialized[key] = [serialize_document(item) if isinstance(item, dict) else str(item) if isinstance(item, ObjectId) else item for item in value]
        elif isinstance(value, dict):
            serialized[key] = serialize_document(value)
        else:
            serialized[key] = value
    return serialized


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
