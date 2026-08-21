from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.db.mongo import check_mongo_health


router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/ready")
async def readiness_check():
    if not await check_mongo_health():
        raise HTTPException(status_code=503, detail={"status": "not_ready", "database": "unavailable"})
    return {
        "status": "ready",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "connected",
    }
