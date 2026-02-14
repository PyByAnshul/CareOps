from datetime import date, datetime, time

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import relationship

from app.core.db import Base


class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)  # nullable for backward compatibility
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    booking_date = Column(Date, nullable=False)
    booking_time = Column(Time, nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending, confirmed, cancelled, completed
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    service = relationship("Service", foreign_keys=[service_id])
    webex_meeting = relationship("WebexMeeting", back_populates="booking", uselist=False, lazy="select")
