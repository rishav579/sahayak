from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


client: AsyncIOMotorClient | None = None


async def connect_to_mongo():
    global client
    client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
    await client.admin.command("ping")


async def close_mongo_connection():
    global client
    if client:
        client.close()
        client = None


def get_database():
    if client is None:
        raise RuntimeError("MongoDB client is not initialized")
    return client[settings.mongodb_db]
