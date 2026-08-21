from __future__ import annotations

import asyncio
import logging

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


logger = logging.getLogger(__name__)
client: AsyncIOMotorClient | None = None
mongo_ready = False


async def connect_to_mongo() -> None:
    global client, mongo_ready
    last_error: Exception | None = None
    for attempt in range(1, max(1, settings.mongodb_connect_retries) + 1):
        candidate = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
        try:
            await candidate.admin.command("ping")
        except Exception as exc:
            last_error = exc
            candidate.close()
            logger.warning("MongoDB startup attempt %s/%s failed", attempt, settings.mongodb_connect_retries)
            if attempt < max(1, settings.mongodb_connect_retries):
                await asyncio.sleep(max(0.0, settings.mongodb_retry_delay_seconds))
            continue

        client = candidate
        mongo_ready = True
        logger.info("MongoDB connection established")
        return

    mongo_ready = False
    raise RuntimeError("MongoDB unavailable after bounded startup retries") from last_error


async def close_mongo_connection() -> None:
    global client, mongo_ready
    if client:
        client.close()
    client = None
    mongo_ready = False


def get_database():
    if client is None or not mongo_ready:
        raise RuntimeError("MongoDB is not ready")
    return client[settings.mongodb_db]


async def check_mongo_health() -> bool:
    if client is None or not mongo_ready:
        return False
    try:
        result = await client.admin.command("ping")
        return result.get("ok") == 1.0
    except Exception:
        logger.exception("MongoDB health check failed")
        return False
