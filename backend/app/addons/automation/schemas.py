from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel


class AutomationEventLogResponse(BaseModel):
    id: int
    workspace_id: int
    event_type: str
    entity_type: str
    entity_id: int
    actions_taken: Dict[str, Any] | None
    status: str
    error_message: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True
