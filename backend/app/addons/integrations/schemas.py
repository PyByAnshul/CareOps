from typing import Any, Dict

from pydantic import BaseModel, EmailStr


class IntegrationCreate(BaseModel):
    integration_type: str
    provider: str
    config: Dict[str, Any]


class IntegrationResponse(BaseModel):
    id: int
    workspace_id: int
    integration_type: str
    provider: str
    config: Dict[str, Any]
    is_active: bool
    
    class Config:
        from_attributes = True


class TestEmailRequest(BaseModel):
    to_email: EmailStr
    subject: str = "Test Email from CareOps"
    body: str = "This is a test email."
