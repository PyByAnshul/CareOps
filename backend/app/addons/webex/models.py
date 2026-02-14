from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.db import Base


class WebexMeeting(Base):
    __tablename__ = "webex_meetings"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    
    meeting_id = Column(String(255), nullable=False)
    meeting_number = Column(String(100), nullable=True)
    meeting_link = Column(Text, nullable=False)
    password = Column(String(100), nullable=True)
    host_key = Column(String(100), nullable=True)
    
    title = Column(String(255), nullable=False)
    start_time = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workspace = relationship("Workspace")
    booking = relationship("Booking", back_populates="webex_meeting")
