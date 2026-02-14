from datetime import datetime

from pydantic import BaseModel


class CalendarSettingsUpdate(BaseModel):
    auto_send_invites: bool | None = None
    include_description: bool | None = None
    email_template: str | None = None


class CalendarSettingsResponse(BaseModel):
    id: int
    workspace_id: int
    auto_send_invites: bool
    include_description: bool
    email_template: str | None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
