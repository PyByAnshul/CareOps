from datetime import date, datetime, time

from pydantic import BaseModel, EmailStr


class BookingCreate(BaseModel):
    service_id: int
    customer_name: str
    customer_email: EmailStr
    booking_date: date
    booking_time: time
    notes: str | None = None


class BookingUpdate(BaseModel):
    customer_name: str | None = None
    customer_email: EmailStr | None = None
    booking_date: date | None = None
    booking_time: time | None = None
    notes: str | None = None


class ServiceInfo(BaseModel):
    id: int
    name: str
    duration_minutes: int
    
    class Config:
        from_attributes = True


class BookingResponse(BaseModel):
    id: int
    workspace_id: int
    service_id: int | None
    service: ServiceInfo | None = None
    customer_name: str
    customer_email: str
    booking_date: date
    booking_time: time
    status: str
    notes: str | None
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True
