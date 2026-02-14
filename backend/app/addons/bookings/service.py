from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.addons.bookings.models import Booking
from app.addons.bookings.schemas import BookingCreate, BookingUpdate
from app.addons.services.utils import is_time_slot_available
from app.core.events.emitter import event_emitter


class BookingService:
    def __init__(self, db: Session, workspace_id: int, user_id: int):
        self.db = db
        self.workspace_id = workspace_id
        self.user_id = user_id
    
    def create_booking(self, booking_data: BookingCreate) -> Booking:
        # Validate availability
        is_available, error_msg = is_time_slot_available(
            self.db,
            self.workspace_id,
            booking_data.service_id,
            booking_data.booking_date,
            booking_data.booking_time,
        )
        
        if not is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
        
        # Create or update contact for customer
        self._create_or_update_contact(
            booking_data.customer_name,
            booking_data.customer_email
        )
        
        booking = Booking(
            workspace_id=self.workspace_id,
            service_id=booking_data.service_id,
            customer_name=booking_data.customer_name,
            customer_email=booking_data.customer_email,
            booking_date=booking_data.booking_date,
            booking_time=booking_data.booking_time,
            notes=booking_data.notes,
            status="pending",
            created_by=self.user_id,
        )
        
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        
        # Emit event
        event_emitter.emit("booking.created", {
            "booking_id": booking.id,
            "workspace_id": self.workspace_id,
            "customer_email": booking.customer_email,
            "booking_date": str(booking.booking_date),
            "booking_time": str(booking.booking_time),
        })
        
        return booking
    
    def _create_or_update_contact(self, customer_name: str, customer_email: str) -> None:
        """Create or update contact for customer."""
        from app.addons.contacts.models import Partner
        
        # Check if contact already exists
        existing_contact = self.db.query(Partner).filter(
            Partner.workspace_id == self.workspace_id,
            Partner.email == customer_email
        ).first()
        
        if not existing_contact:
            # Create new contact
            contact = Partner(
                workspace_id=self.workspace_id,
                name=customer_name,
                email=customer_email,
                partner_type="customer",
                is_active=True
            )
            self.db.add(contact)
            self.db.flush()
        elif existing_contact.name != customer_name:
            # Update name if changed
            existing_contact.name = customer_name
            self.db.flush()
    
    def list_bookings(self, status: str | None = None) -> List[Booking]:
        from sqlalchemy.orm import joinedload
        query = self.db.query(Booking).options(
            joinedload(Booking.service)
        ).filter(
            Booking.workspace_id == self.workspace_id
        )
        
        if status:
            query = query.filter(Booking.status == status)
        
        return query.all()
    
    def get_booking(self, booking_id: int) -> Booking:
        from sqlalchemy.orm import joinedload
        booking = self.db.query(Booking).options(
            joinedload(Booking.service)
        ).filter(
            Booking.id == booking_id,
            Booking.workspace_id == self.workspace_id,
        ).first()
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )
        
        return booking
    
    def update_booking(self, booking_id: int, booking_data: BookingUpdate) -> Booking:
        booking = self.get_booking(booking_id)
        
        # If updating date/time, validate availability
        if booking_data.booking_date or booking_data.booking_time:
            new_date = booking_data.booking_date or booking.booking_date
            new_time = booking_data.booking_time or booking.booking_time
            service_id = booking.service_id
            
            if service_id:
                is_available, error_msg = is_time_slot_available(
                    self.db,
                    self.workspace_id,
                    service_id,
                    new_date,
                    new_time,
                    exclude_booking_id=booking_id,
                )
                
                if not is_available:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=error_msg,
                    )
        
        update_data = booking_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(booking, field, value)
        
        self.db.commit()
        self.db.refresh(booking)
        
        return booking
    
    def delete_booking(self, booking_id: int) -> None:
        booking = self.get_booking(booking_id)
        self.db.delete(booking)
        self.db.commit()
    
    def confirm_booking(self, booking_id: int) -> Booking:
        booking = self.get_booking(booking_id)
        booking.status = "confirmed"
        self.db.commit()
        self.db.refresh(booking)
        
        # Create Webex meeting
        meeting_link = self._create_webex_meeting(booking)
        
        # Emit event to send confirmation email with calendar invite and meeting link
        event_emitter.emit("booking.confirmed", {
            "booking_id": booking.id,
            "workspace_id": self.workspace_id,
            "customer_email": booking.customer_email,
            "customer_name": booking.customer_name,
            "booking_date": str(booking.booking_date),
            "booking_time": str(booking.booking_time),
            "meeting_link": meeting_link,
        })
        
        return booking
    
    def _create_webex_meeting(self, booking: Booking) -> str:
        """Create Webex meeting for booking."""
        from app.addons.webex.service import WebexService
        from app.addons.webex.schemas import WebexMeetingCreate
        from datetime import datetime
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            webex_service = WebexService(self.db, self.workspace_id)
            
            # Check if meeting already exists
            existing_meeting = webex_service.get_meeting_by_booking(booking.id)
            if existing_meeting:
                logger.info(f"Webex meeting already exists for booking {booking.id}")
                return existing_meeting.meeting_link
            
            # Combine date and time
            start_time = datetime.combine(booking.booking_date, booking.booking_time)
            duration = booking.service.duration_minutes if booking.service else 60
            
            meeting_data = WebexMeetingCreate(
                booking_id=booking.id,
                title=f"{booking.service.name if booking.service else 'Appointment'} - {booking.customer_name}",
                start_time=start_time,
                duration=duration
            )
            
            logger.info(f"Creating Webex meeting for booking {booking.id}")
            meeting = webex_service.create_meeting(meeting_data)
            logger.info(f"Webex meeting created: {meeting.meeting_link}")
            return meeting.meeting_link
        except Exception as e:
            # If Webex fails, log and continue without meeting link
            logger.warning(f"Failed to create Webex meeting for booking {booking.id}: {str(e)}")
            return ""
    
    def cancel_booking(self, booking_id: int) -> Booking:
        booking = self.get_booking(booking_id)
        booking.status = "cancelled"
        self.db.commit()
        self.db.refresh(booking)
        
        # Emit event to send cancellation email
        event_emitter.emit("booking.cancelled", {
            "booking_id": booking.id,
            "workspace_id": self.workspace_id,
            "customer_email": booking.customer_email,
            "customer_name": booking.customer_name,
            "booking_date": str(booking.booking_date),
            "booking_time": str(booking.booking_time),
        })
        
        return booking
    
    def complete_booking(self, booking_id: int) -> Booking:
        booking = self.get_booking(booking_id)
        booking.status = "completed"
        self.db.commit()
        self.db.refresh(booking)
        return booking
