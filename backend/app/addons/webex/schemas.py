from datetime import datetime
from pydantic import BaseModel


class WebexMeetingCreate(BaseModel):
    booking_id: int | None = None
    title: str
    start_time: datetime
    duration: int


class WebexMeetingResponse(BaseModel):
    id: int
    booking_id: int | None
    meeting_id: str
    meeting_link: str
    password: str | None
    title: str
    start_time: datetime
    duration: int
    
    class Config:
        from_attributes = True
