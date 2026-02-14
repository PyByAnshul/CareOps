from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class PartnerCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    partner_type: str = "customer"
    notes: Optional[str] = None


class PartnerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    partner_type: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class PartnerResponse(BaseModel):
    id: int
    workspace_id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    address: Optional[str]
    partner_type: str
    has_portal_access: bool
    user_id: Optional[int]
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GrantPortalAccess(BaseModel):
    email: Optional[EmailStr] = None  # Required only when contact has no email
    password: str
