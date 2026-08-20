from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.core.security import create_access_token
from app.db.mongo import get_database
from app.utils.helpers import serialize_document


GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


async def verify_google_credential(credential: str):
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(GOOGLE_TOKENINFO_URL, params={"id_token": credential})
        response.raise_for_status()
        payload = response.json()

    audience = payload.get("aud")
    if settings.google_client_id and audience != settings.google_client_id:
        raise ValueError("Google token audience mismatch")
    return payload


async def login_with_google(credential: str):
    profile = await verify_google_credential(credential)

    db = get_database()
    users = db.users

    user = await users.find_one({"google_id": profile["sub"]})
    now = datetime.now(timezone.utc)

    if user:
        await users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "email": profile.get("email"),
                    "name": profile.get("name"),
                    "picture": profile.get("picture"),
                }
            },
        )
        user = await users.find_one({"_id": user["_id"]})
    else:
        payload = {
            "google_id": profile["sub"],
            "email": profile.get("email"),
            "name": profile.get("name"),
            "picture": profile.get("picture"),
            "created_at": now,
        }
        result = await users.insert_one(payload)
        user = await users.find_one({"_id": result.inserted_id})

    serialized_user = serialize_document(user)
    token = create_access_token(
        {
            "sub": serialized_user["_id"],
            "email": serialized_user["email"],
            "name": serialized_user["name"],
        }
    )

    return {"access_token": token, "token_type": "bearer", "user": serialized_user}
