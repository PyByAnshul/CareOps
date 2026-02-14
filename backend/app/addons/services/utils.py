from datetime import date, datetime, time, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.addons.bookings.models import Booking
from app.addons.services.models import Service, ServiceAvailability


def is_time_slot_available(
    db: Session,
    workspace_id: int,
    service_id: int,
    booking_date: date,
    booking_time: time,
    exclude_booking_id: Optional[int] = None,
) -> tuple[bool, str]:
    """
    Check if a time slot is available for booking.
    
    Returns:
        (is_available, error_message)
    """
    # Get service
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.workspace_id == workspace_id,
        Service.is_active == True,
    ).first()
    
    if not service:
        return False, "Service not found or inactive"
    
    # Check if day/time is within service availability
    day_of_week = booking_date.weekday()
    
    availability = db.query(ServiceAvailability).filter(
        ServiceAvailability.service_id == service_id,
        ServiceAvailability.day_of_week == day_of_week,
    ).all()
    
    if not availability:
        return False, f"Service not available on this day"
    
    # Check if booking time falls within any availability window
    time_in_window = False
    for avail in availability:
        if avail.start_time <= booking_time < avail.end_time:
            time_in_window = True
            break
    
    if not time_in_window:
        return False, "Time slot outside service hours"
    
    # Calculate booking end time
    booking_datetime = datetime.combine(booking_date, booking_time)
    booking_end = booking_datetime + timedelta(minutes=service.duration_minutes)
    booking_end_time = booking_end.time()
    
    # Check for overlapping bookings
    query = db.query(Booking).filter(
        Booking.workspace_id == workspace_id,
        Booking.booking_date == booking_date,
        Booking.status.in_(["pending", "confirmed"]),
    )
    
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    
    existing_bookings = query.all()
    
    for existing in existing_bookings:
        # Get existing booking service
        existing_service = db.query(Service).filter(Service.id == existing.service_id).first()
        if not existing_service:
            continue
        
        # Calculate existing booking end time
        existing_datetime = datetime.combine(existing.booking_date, existing.booking_time)
        existing_end = existing_datetime + timedelta(minutes=existing_service.duration_minutes)
        existing_end_time = existing_end.time()
        
        # Check for overlap
        if not (booking_end_time <= existing.booking_time or booking_time >= existing_end_time):
            return False, f"Time slot conflicts with existing booking"
    
    return True, ""
