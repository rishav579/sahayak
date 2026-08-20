from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class GoogleAuthRequest(BaseModel):
    credential: str


class UserOut(BaseModel):
    id: str = Field(alias="_id")
    google_id: str
    email: EmailStr
    name: str
    picture: str | None = None
    created_at: datetime

    model_config = {"populate_by_name": True}


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ActionItemBase(BaseModel):
    task: str
    assignee: str | None = None
    deadline: str | None = None
    status: Literal["pending", "completed", "overdue"] = "pending"
    reminder_sent: bool = False


class ActionItemOut(ActionItemBase):
    id: str = Field(alias="_id")
    meeting_id: str
    created_at: datetime

    model_config = {"populate_by_name": True}


class MeetingOut(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    title: str
    audio_url: str | None = None
    transcript: str
    action_items: list[ActionItemOut] = []
    created_at: datetime

    model_config = {"populate_by_name": True}


class UploadResponse(BaseModel):
    meeting: MeetingOut
    transcript: str
    action_items: list[ActionItemOut]


class ReminderResponse(BaseModel):
    message: str
    status: str
    action_item: ActionItemOut
