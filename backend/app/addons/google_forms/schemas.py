from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel


class FieldMapping(BaseModel):
    """Maps a Google Form field to a CareOps booking field."""
    google_field: str  # Google Form question title
    careops_field: str  # CareOps field name (customer_name, customer_email, etc.)
    is_required: bool = False


class GoogleFormIntegrationCreate(BaseModel):
    name: str
    google_form_id: str
    google_form_url: str
    field_mappings: Dict[str, str]  # {google_field: careops_field}


class GoogleFormIntegrationUpdate(BaseModel):
    name: str | None = None
    google_form_url: str | None = None
    field_mappings: Dict[str, str] | None = None
    is_active: bool | None = None


class GoogleFormIntegrationResponse(BaseModel):
    id: int
    workspace_id: int
    name: str
    google_form_id: str
    google_form_url: str
    webhook_secret: str
    field_mappings: Dict[str, str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WebhookPayload(BaseModel):
    """Incoming webhook data from Google Forms."""
    email: str
    responses: Dict[str, Any]  # {question_title: answer}


class GoogleFormSubmissionResponse(BaseModel):
    id: int
    integration_id: int
    booking_id: int | None
    raw_data: Dict[str, Any]
    mapped_data: Dict[str, Any]
    status: str
    error_message: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True
