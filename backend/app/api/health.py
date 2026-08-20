from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.db.mongo import get_database

router = APIRouter()


@router.get('/health')
async def health_check():
    try:
        db = get_database()
        ping_result = await db.command('ping')
        return {
            'status': 'ok',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'database': 'connected' if ping_result.get('ok') == 1.0 else 'degraded',
        }
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                'status': 'error',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'database': 'disconnected',
                'message': str(exc),
            },
        ) from exc
