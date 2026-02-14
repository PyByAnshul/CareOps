from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    workspace_id: int
    type: str
    severity: str
    title: str
    message: str
    link: str | None
    is_dismissed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
