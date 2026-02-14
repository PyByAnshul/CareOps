from datetime import datetime

from pydantic import BaseModel


class WorkspaceCreate(BaseModel):
    name: str
    timezone: str = "UTC"


class WorkspaceResponse(BaseModel):
    id: int
    name: str
    timezone: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
