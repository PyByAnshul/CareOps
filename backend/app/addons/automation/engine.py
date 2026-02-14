import logging
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.addons.automation.models import AutomationEventLog

logger = logging.getLogger(__name__)


class AutomationEngine:
    """
    Core automation engine that processes events and enqueues tasks.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def process_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        workspace_id: int,
        entity_type: str,
        entity_id: int,
    ) -> None:
        """
        Process an event by enqueuing background tasks.
        """
        logger.info(f"Processing automation for event: {event_type}")
        
        # Create log entry immediately
        log_entry = AutomationEventLog(
            workspace_id=workspace_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actions_taken=[],
            status="pending",
            error_message=None,
        )
        
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        
        logger.info(f"Automation log {log_entry.id} created")
        
        # Enqueue tasks based on event type
        try:
            self._enqueue_tasks(event_type, event_data, log_entry.id)
            
            # Update status to processing
            log_entry.status = "processing"
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to enqueue tasks: {str(e)}")
            log_entry.status = "failed"
            log_entry.error_message = str(e)
            self.db.commit()
    
    def _enqueue_tasks(self, event_type: str, event_data: Dict[str, Any], log_id: int) -> None:
        """Enqueue background tasks for the event."""
        from app.addons.automation.tasks import send_confirmation_task, notify_staff_task
        
        if event_type == "booking.created":
            send_confirmation_task.delay(event_data, log_id)
            notify_staff_task.delay(event_data, log_id)
            logger.info(f"Enqueued tasks for {event_type}")
        
        elif event_type == "booking.confirmed":
            send_confirmation_task.delay(event_data, log_id)
            logger.info(f"Enqueued confirmation task for {event_type}")
        
        elif event_type == "booking.cancelled":
            notify_staff_task.delay(event_data, log_id)
            logger.info(f"Enqueued tasks for {event_type}")
        
        else:
            logger.debug(f"No tasks configured for event: {event_type}")


def get_automation_engine(db: Session) -> AutomationEngine:
    """Factory function to get automation engine instance."""
    return AutomationEngine(db)
