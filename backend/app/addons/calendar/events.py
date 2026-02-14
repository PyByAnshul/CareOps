"""Calendar event handlers."""
import logging

from app.core.db import SessionLocal

logger = logging.getLogger(__name__)


def handle_booking_created(event_name: str, data: dict):
    """Send calendar invite when booking is created."""
    if event_name != "booking.created":
        return
    
    booking_id = data.get("booking_id")
    workspace_id = data.get("workspace_id")
    
    if not booking_id or not workspace_id:
        return
    
    db = SessionLocal()
    try:
        from app.addons.calendar.service import CalendarService
        
        service = CalendarService(db, workspace_id)
        settings = service.get_or_create_settings()
        
        # Only send if auto-send is enabled
        if settings.auto_send_invites:
            result = service.send_calendar_invite(booking_id)
            if result["success"]:
                logger.info(f"Calendar invite sent for booking {booking_id}")
            else:
                logger.warning(f"Failed to send calendar invite: {result['message']}")
    
    except Exception as e:
        logger.error(f"Error sending calendar invite: {str(e)}")
    
    finally:
        db.close()


def handle_booking_confirmed(event_name: str, data: dict):
    """Send confirmation email with calendar invite."""
    if event_name != "booking.confirmed":
        return
    
    booking_id = data.get("booking_id")
    workspace_id = data.get("workspace_id")
    
    if not booking_id or not workspace_id:
        return
    
    db = SessionLocal()
    try:
        from app.addons.calendar.service import CalendarService
        
        service = CalendarService(db, workspace_id)
        result = service.send_calendar_invite(booking_id, subject="Booking Confirmed")
        
        if result["success"]:
            logger.info(f"Confirmation email sent for booking {booking_id}")
        else:
            logger.warning(f"Failed to send confirmation: {result['message']}")
    
    except Exception as e:
        logger.error(f"Error sending confirmation: {str(e)}")
    
    finally:
        db.close()


def handle_booking_cancelled(event_name: str, data: dict):
    """Send cancellation email."""
    if event_name != "booking.cancelled":
        return
    
    booking_id = data.get("booking_id")
    workspace_id = data.get("workspace_id")
    customer_email = data.get("customer_email")
    customer_name = data.get("customer_name")
    
    if not all([booking_id, workspace_id, customer_email]):
        return
    
    db = SessionLocal()
    try:
        from app.addons.integrations.service import IntegrationService
        
        service = IntegrationService(db, workspace_id)
        email_provider = service.get_email_provider()
        
        if not email_provider:
            logger.warning("No email provider configured")
            return
        
        subject = "Booking Cancelled"
        body = f"""Dear {customer_name},

Your booking has been cancelled.

If you have any questions, please contact us.

Best regards
"""
        
        email_provider.send_email(
            to_email=customer_email,
            subject=subject,
            body=body
        )
        
        logger.info(f"Cancellation email sent for booking {booking_id}")
    
    except Exception as e:
        logger.error(f"Error sending cancellation email: {str(e)}")
    
    finally:
        db.close()


# Register the handlers
from app.core.events.emitter import event_emitter
event_emitter.register_handler(handle_booking_created)
event_emitter.register_handler(handle_booking_confirmed)
event_emitter.register_handler(handle_booking_cancelled)
