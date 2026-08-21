import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse

from app.api.deps import get_current_user
from app.core.config import settings
from app.models.schemas import AuthResponse, GoogleAuthRequest, ReminderResponse, UploadResponse
from app.services.action_item_service import list_action_items, mark_action_item_complete, send_mock_reminder
from app.services.auth_service import login_with_google
from app.services.media_storage import LocalMediaStorage, media_content_type
from app.services.meeting_service import create_meeting_from_upload, get_meeting_by_id, get_meeting_for_media, get_meetings_for_user


logger = logging.getLogger(__name__)
router = APIRouter()
storage = LocalMediaStorage(settings.upload_dir)


@router.post("/auth/google", response_model=AuthResponse)
async def google_auth(payload: GoogleAuthRequest):
    try:
        return await login_with_google(payload.credential)
    except Exception as exc:
        logger.exception("Google login failed")
        raise HTTPException(status_code=400, detail="Google login failed") from exc


@router.post("/upload", response_model=UploadResponse)
async def upload_meeting(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(..., max_length=200),
    current_user: dict = Depends(get_current_user),
):
    stored = await storage.save_upload(file, settings.max_file_size_mb * 1024 * 1024)
    try:
        base_url = str(request.base_url).rstrip("/")
        return await create_meeting_from_upload(
            current_user["sub"],
            title.strip(),
            str(stored.path),
            stored.filename,
            base_url,
            stored.content_type,
        )
    except Exception:
        storage.delete(stored.filename)
        logger.exception("Meeting processing failed")
        raise HTTPException(status_code=500, detail="Meeting processing failed")


@router.get("/media/{filename}")
async def get_media(filename: str, current_user: dict = Depends(get_current_user)):
    meeting = await get_meeting_for_media(filename, current_user["sub"])
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    path = storage.resolve(filename)
    if path is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    return FileResponse(
        path,
        media_type=media_content_type(path, meeting.get("media_content_type")),
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.get("/meetings")
async def get_meetings(current_user: dict = Depends(get_current_user)):
    return await get_meetings_for_user(current_user["sub"])


@router.get("/meetings/{meeting_id}")
async def get_meeting(meeting_id: str, current_user: dict = Depends(get_current_user)):
    try:
        meeting = await get_meeting_by_id(meeting_id, current_user["sub"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid meeting id") from exc
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    return meeting


@router.get("/action-items")
async def get_action_items(status: str | None = None, current_user: dict = Depends(get_current_user)):
    return await list_action_items(current_user["sub"], status)


@router.post("/action-items/{action_item_id}/complete")
async def complete_action_item(action_item_id: str, current_user: dict = Depends(get_current_user)):
    try:
        item = await mark_action_item_complete(action_item_id, current_user["sub"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid action item id") from exc
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    return item


@router.post("/send-reminder/{action_item_id}", response_model=ReminderResponse)
async def send_reminder(action_item_id: str, current_user: dict = Depends(get_current_user)):
    try:
        item = await send_mock_reminder(action_item_id, current_user["sub"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid action item id") from exc
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    return {
        "message": "Mock WhatsApp reminder sent successfully.",
        "status": "sent",
        "action_item": item,
    }
