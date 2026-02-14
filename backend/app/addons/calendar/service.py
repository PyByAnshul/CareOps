from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.addons.bookings.models import Booking
from app.addons.calendar.models import CalendarSettings


class CalendarService:
    def __init__(self, db: Session, workspace_id: int):
        self.db = db
        self.workspace_id = workspace_id
    
    def get_or_create_settings(self) -> CalendarSettings:
        """Get or create calendar settings for workspace."""
        settings = self.db.query(CalendarSettings).filter(
            CalendarSettings.workspace_id == self.workspace_id
        ).first()
        
        if not settings:
            settings = CalendarSettings(
                workspace_id=self.workspace_id,
                auto_send_invites=True,
                include_description=True,
            )
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        
        return settings
    
    def update_settings(self, auto_send_invites: Optional[bool] = None, 
                       include_description: Optional[bool] = None,
                       email_template: Optional[str] = None) -> CalendarSettings:
        """Update calendar settings."""
        settings = self.get_or_create_settings()
        
        if auto_send_invites is not None:
            settings.auto_send_invites = auto_send_invites
        if include_description is not None:
            settings.include_description = include_description
        if email_template is not None:
            settings.email_template = email_template
        
        self.db.commit()
        self.db.refresh(settings)
        
        return settings
    
    def generate_ics(self, booking: Booking) -> str:
        """Generate iCalendar (.ics) content for booking."""
        # Combine date and time
        start_dt = datetime.combine(booking.booking_date, booking.booking_time)
        
        # Default duration: 1 hour or service duration
        duration_minutes = 60
        if booking.service and hasattr(booking.service, 'duration_minutes'):
            duration_minutes = booking.service.duration_minutes
        
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        # Format datetime for iCalendar (UTC)
        def format_dt(dt):
            return dt.strftime('%Y%m%dT%H%M%S')
        
        # Build description
        description = f"Booking with {booking.customer_name}"
        if booking.service:
            description += f"\\nService: {booking.service.name}"
        if booking.notes:
            description += f"\\nNotes: {booking.notes}"
        
        # Generate unique UID
        uid = f"booking-{booking.id}@careops"
        
        # Build iCalendar content
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CareOps//Booking System//EN
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{format_dt(datetime.utcnow())}
DTSTART:{format_dt(start_dt)}
DTEND:{format_dt(end_dt)}
SUMMARY:{booking.service.name if booking.service else 'Booking'}
DESCRIPTION:{description}
ORGANIZER:mailto:noreply@careops.com
ATTENDEE;CN={booking.customer_name};RSVP=TRUE:mailto:{booking.customer_email}
STATUS:CONFIRMED
SEQUENCE:0
END:VEVENT
END:VCALENDAR"""
        
        return ics_content
    
    def send_calendar_invite(self, booking_id: int) -> dict:
        """Send calendar invite for booking."""
        from app.addons.integrations.providers.factory import ProviderFactory
        
        # Get booking
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return {"success": False, "message": "Booking not found"}
        
        # Check settings
        settings = self.get_or_create_settings()
        if not settings.auto_send_invites:
            return {"success": False, "message": "Auto-send disabled"}
        
        # Get email provider
        provider = ProviderFactory.get_email_provider(self.workspace_id, self.db)
        if not provider:
            return {"success": False, "message": "No email provider configured"}
        
        # Generate iCalendar content
        ics_content = self.generate_ics(booking)
        
        # Build email
        subject = f"Booking Confirmation - {booking.service.name if booking.service else 'Appointment'}"
        
        body = f"""
<html>
<body>
<h2>Booking Confirmation</h2>
<p>Dear {booking.customer_name},</p>
<p>Your booking has been confirmed with the following details:</p>
<ul>
<li><strong>Service:</strong> {booking.service.name if booking.service else 'N/A'}</li>
<li><strong>Date:</strong> {booking.booking_date.strftime('%B %d, %Y')}</li>
<li><strong>Time:</strong> {booking.booking_time.strftime('%I:%M %p')}</li>
</ul>
{f'<p><strong>Notes:</strong> {booking.notes}</p>' if booking.notes else ''}
<p>A calendar invite is attached to this email. Please add it to your calendar.</p>
<p>If you need to reschedule or cancel, please contact us.</p>
<p>Best regards,<br>CareOps Team</p>
</body>
</html>
"""
        
        # Send email with attachment
        result = self._send_email_with_ics(
            provider, 
            booking.customer_email, 
            subject, 
            body, 
            ics_content
        )
        
        return result
    
    def _send_email_with_ics(self, provider, to_email: str, subject: str, 
                            body: str, ics_content: str) -> dict:
        """Send email with iCalendar attachment."""
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders
        import smtplib
        
        try:
            # Create message
            msg = MIMEMultipart('mixed')
            msg['Subject'] = subject
            msg['To'] = to_email
            msg['From'] = provider.config.get('from_email', 'noreply@careops.com')
            
            # Add HTML body
            msg.attach(MIMEText(body, 'html'))
            
            # Add iCalendar attachment
            ics_part = MIMEBase('text', 'calendar', method='REQUEST', name='invite.ics')
            ics_part.set_payload(ics_content)
            encoders.encode_base64(ics_part)
            ics_part.add_header('Content-Disposition', 'attachment', filename='invite.ics')
            msg.attach(ics_part)
            
            # Send via SMTP
            if hasattr(provider, 'config'):
                use_tls = provider.config.get('use_tls', True)
                
                if use_tls:
                    server = smtplib.SMTP(provider.config['host'], provider.config['port'])
                    server.starttls()
                else:
                    server = smtplib.SMTP_SSL(provider.config['host'], provider.config['port'])
                
                server.login(provider.config['username'], provider.config['password'])
                server.send_message(msg)
                server.quit()
                
                return {"success": True, "message": f"Calendar invite sent to {to_email}"}
            else:
                return {"success": False, "message": "Provider not configured for attachments"}
        
        except Exception as e:
            return {"success": False, "message": str(e)}
