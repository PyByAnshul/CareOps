import logging
import time
from typing import Any, Dict

from app.core.db import SessionLocal
from app.core.jobs.base_tasks import BaseTask
from app.core.jobs.celery_app import celery_app

# Import models so SQLAlchemy can resolve Booking relationships in the worker process
from app.addons.bookings.models import Booking  # noqa: F401
from app.addons.services.models import Service  # noqa: F401
from app.addons.webex.models import WebexMeeting  # noqa: F401

logger = logging.getLogger(__name__)


@celery_app.task(base=BaseTask, bind=True, max_retries=3)
def send_confirmation_task(self, event_data: Dict[str, Any], log_id: int) -> Dict[str, Any]:
    """
    Send booking confirmation email with calendar invite using workspace email provider.
    """
    from app.addons.integrations.providers.factory import ProviderFactory
    from datetime import datetime, timedelta
    from icalendar import Calendar, Event as ICalEvent
    import pytz
    
    db = SessionLocal()
    try:
        customer_email = event_data.get("customer_email")
        customer_name = event_data.get("customer_name", "Customer")
        booking_id = event_data.get("booking_id")
        workspace_id = event_data.get("workspace_id")
        booking_date = event_data.get("booking_date")
        booking_time = event_data.get("booking_time")
        meeting_link = event_data.get("meeting_link", "")
        
        logger.info(f"Sending confirmation email with calendar invite to {customer_email} for booking {booking_id}")
        
        # Get booking details
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        service_name = "Service"
        duration_minutes = 60
        
        if booking and booking.service:
            service_name = booking.service.name
            duration_minutes = booking.service.duration_minutes
        
        # Get email provider for workspace
        provider = ProviderFactory.get_email_provider(workspace_id, db)
        
        if not provider:
            logger.warning(f"No email provider configured for workspace {workspace_id}")
            result = {
                "action": "send_confirmation",
                "status": "failed",
                "message": "No email provider configured",
                "booking_id": booking_id,
            }
            _update_automation_log(log_id, result, failed=True)
            return result
        
        # Create calendar invite
        cal = Calendar()
        cal.add('prodid', '-//CareOps Booking System//careops.com//')
        cal.add('version', '2.0')
        cal.add('method', 'REQUEST')
        
        event = ICalEvent()
        event.add('summary', f'{service_name} - Booking #{booking_id}')
        event.add('description', f'Your booking has been confirmed.\n\nBooking ID: {booking_id}\nService: {service_name}')
        
        # Parse date and time
        start_dt = datetime.strptime(f"{booking_date} {booking_time}", "%Y-%m-%d %H:%M:%S")
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        event.add('dtstart', start_dt)
        event.add('dtend', end_dt)
        event.add('dtstamp', datetime.now())
        event.add('uid', f'booking-{booking_id}@careops.com')
        event.add('status', 'CONFIRMED')
        event.add('sequence', 0)
        event.add('organizer', 'noreply@careops.com')
        event.add('attendee', customer_email)
        
        cal.add_component(event)
        ics_content = cal.to_ical().decode('utf-8')
        
        # Compose email
        subject = f"Booking Confirmed - {service_name}"
        
        meeting_info = ""
        if meeting_link:
            meeting_info = f"""

Webex Meeting Link:
{meeting_link}

Join the meeting at the scheduled time using the link above.
"""
        
        body = f"""
Dear {customer_name},

Your booking has been confirmed!

Booking Details:
- Booking ID: #{booking_id}
- Service: {service_name}
- Date: {booking_date}
- Time: {booking_time}
- Duration: {duration_minutes} minutes{meeting_info}

A calendar invite is attached to this email. Please add it to your calendar.

Thank you for choosing our service.

Best regards,
CareOps Team
        """
        
        # Send email with calendar attachment
        email_result = provider.send_email(
            customer_email, 
            subject, 
            body,
            attachments=[{
                'filename': f'booking-{booking_id}.ics',
                'content': ics_content,
                'content_type': 'text/calendar'
            }]
        )
        
        if email_result["success"]:
            result = {
                "action": "send_confirmation",
                "status": "success",
                "message": f"Confirmation with calendar invite sent to {customer_email}",
                "booking_id": booking_id,
            }
            _update_automation_log(log_id, result)
        else:
            result = {
                "action": "send_confirmation",
                "status": "failed",
                "message": email_result["message"],
                "booking_id": booking_id,
            }
            _update_automation_log(log_id, result, failed=True)
        
        return result
    
    except Exception as e:
        logger.error(f"send_confirmation_task failed: {str(e)}")
        result = {
            "action": "send_confirmation",
            "status": "failed",
            "error": str(e),
        }
        _update_automation_log(log_id, result, failed=True)
        raise
    finally:
        db.close()


@celery_app.task(base=BaseTask, bind=True, max_retries=3)
def notify_staff_task(self, event_data: Dict[str, Any], log_id: int) -> Dict[str, Any]:
    """
    Mock task: Notify staff about booking.
    """
    try:
        booking_id = event_data.get("booking_id")
        workspace_id = event_data.get("workspace_id")
        
        logger.info(f"[MOCK] Notifying staff about booking {booking_id} in workspace {workspace_id}")
        
        # Simulate processing
        time.sleep(0.5)
        
        result = {
            "action": "notify_staff",
            "status": "success",
            "message": f"Staff notified about booking {booking_id}",
            "booking_id": booking_id,
        }
        
        # Update log
        _update_automation_log(log_id, result)
        
        return result
    
    except Exception as e:
        logger.error(f"notify_staff_task failed: {str(e)}")
        result = {
            "action": "notify_staff",
            "status": "failed",
            "error": str(e),
        }
        _update_automation_log(log_id, result, failed=True)
        raise


def _update_automation_log(log_id: int, action_result: Dict[str, Any], failed: bool = False) -> None:
    """Update automation log with task result."""
    from app.addons.automation.models import AutomationEventLog
    from app.addons.alerts.utils import create_alert
    
    db = SessionLocal()
    try:
        log = db.query(AutomationEventLog).filter(AutomationEventLog.id == log_id).first()
        if log:
            actions_taken = log.actions_taken or []
            actions_taken.append(action_result)
            log.actions_taken = actions_taken
            
            # Update status based on results
            if failed:
                if log.status == "processing":
                    log.status = "partial"
                
                # Create alert for failed automation
                create_alert(
                    db=db,
                    workspace_id=log.workspace_id,
                    alert_type="automation_failed",
                    severity="warning",
                    title=f"Automation Failed: {log.event_type}",
                    message=f"Action '{action_result.get('action')}' failed: {action_result.get('message', action_result.get('error', 'Unknown error'))}",
                    link=f"/automation/logs/{log_id}",
                )
            else:
                # Check if all actions are complete
                all_success = all(a.get("status") == "success" for a in actions_taken)
                if all_success and log.status == "processing":
                    log.status = "success"
            
            db.commit()
            logger.info(f"Updated automation log {log_id} with status {log.status}")
    except Exception as e:
        logger.error(f"Failed to update automation log: {str(e)}")
    finally:
        db.close()
