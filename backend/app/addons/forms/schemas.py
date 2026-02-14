from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, EmailStr


class FormCreate(BaseModel):
    name: str
    form_type: str = "booking"  # booking, inquiry, quote
    schema: Dict[str, Any]


class FormResponse(BaseModel):
    id: int
    workspace_id: int
    name: str
    form_type: str
    schema: Dict[str, Any]
    is_active: bool
    token: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class FormSubmissionCreate(BaseModel):
    contact_email: EmailStr
    answers: Dict[str, Any]


class FormSubmissionResponse(BaseModel):
    id: int
    form_id: int
    booking_id: int | None
    inquiry_id: int | None
    contact_email: str
    answers: Dict[str, Any]
    status: str
    token: str
    submitted_at: datetime | None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PublicFormResponse(BaseModel):
    """Public form data without sensitive info."""
    form_name: str
    form_type: str
    schema: Dict[str, Any]
    token: str


class InquiryResponse(BaseModel):
    id: int
    workspace_id: int
    form_submission_id: int | None
    customer_name: str
    customer_email: str
    inquiry_type: str
    subject: str | None
    message: str | None
    status: str
    assigned_to: int | None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InquiryUpdate(BaseModel):
    status: str | None = None
    assigned_to: int | None = None
