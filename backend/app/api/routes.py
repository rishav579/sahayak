import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status

from app.api.deps import get_current_user
from app.core.config import settings
from app.models.schemas import AuthResponse, GoogleAuthRequest, ReminderResponse, UploadResponse
from app.services.action_item_service import list_action_items, mark_action_item_complete, send_mock_reminder
from app.services.auth_service import login_with_google
from app.services.meeting_service import create_meeting_from_upload, get_meeting_by_id, get_meetings_for_user

router = APIRouter()

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".mov", ".mpeg", ".webm"}


@router.post("/auth/google", response_model=AuthResponse)
async def google_auth(payload: GoogleAuthRequest):
    try:
        return await login_with_google(payload.credential)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Google login failed: {exc}") from exc


@router.post("/upload", response_model=UploadResponse)
async def upload_meeting(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(...),
    current_user: dict = Depends(get_current_user),
):
    os.makedirs(settings.upload_dir, exist_ok=True)
    extension = os.path.splitext(file.filename or "audio")[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    contents = await file.read()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File exceeds {settings.max_file_size_mb}MB limit")

    unique_name = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(settings.upload_dir, unique_name)
    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    base_url = str(request.base_url).rstrip("/")
    return await create_meeting_from_upload(current_user["sub"], title, file_path, file.filename or unique_name, base_url)


@router.get("/meetings")
async def get_meetings(current_user: dict = Depends(get_current_user)):
    return await get_meetings_for_user(current_user["sub"])


@router.get("/meetings/{meeting_id}")
async def get_meeting(meeting_id: str, current_user: dict = Depends(get_current_user)):
    meeting = await get_meeting_by_id(meeting_id, current_user["sub"])
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    return meeting


@router.get("/action-items")
async def get_action_items(status: str | None = None, current_user: dict = Depends(get_current_user)):
    return await list_action_items(current_user["sub"], status)


@router.post("/action-items/{action_item_id}/complete")
async def complete_action_item(action_item_id: str, current_user: dict = Depends(get_current_user)):
    item = await mark_action_item_complete(action_item_id, current_user["sub"])
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    return item


@router.post("/send-reminder/{action_item_id}", response_model=ReminderResponse)
async def send_reminder(action_item_id: str, current_user: dict = Depends(get_current_user)):
    item = await send_mock_reminder(action_item_id, current_user["sub"])
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    return {
        "message": "Mock WhatsApp reminder sent successfully.",
        "status": "sent",
        "action_item": item,
    }
