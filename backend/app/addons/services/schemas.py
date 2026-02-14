from datetime import datetime, time

from pydantic import BaseModel


class ServiceCreate(BaseModel):
    name: str
    duration_minutes: int


class ServiceResponse(BaseModel):
    id: int
    workspace_id: int
    name: str
    duration_minutes: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AvailabilityCreate(BaseModel):
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time


class AvailabilityResponse(BaseModel):
    id: int
    service_id: int
    day_of_week: int
    start_time: time
    end_time: time
    
    class Config:
        from_attributes = True
