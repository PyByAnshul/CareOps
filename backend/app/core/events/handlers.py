import logging
from typing import Any, Dict

from app.core.db import SessionLocal

logger = logging.getLogger(__name__)


def automation_event_handler(event_name: str, event_data: Dict[str, Any]) -> None:
    """
    Event handler that triggers automation engine.
    """
    from app.addons.automation.engine import get_automation_engine
    
    workspace_id = event_data.get("workspace_id")
    if not workspace_id:
        logger.warning(f"Event {event_name} missing workspace_id, skipping automation")
        return
    
    # Determine entity type and ID from event data
    entity_type = "unknown"
    entity_id = 0
    
    if "booking_id" in event_data:
        entity_type = "booking"
        entity_id = event_data["booking_id"]
    
    # Create a new DB session for automation processing
    db = SessionLocal()
    try:
        engine = get_automation_engine(db)
        engine.process_event(
            event_type=event_name,
            event_data=event_data,
            workspace_id=workspace_id,
            entity_type=entity_type,
            entity_id=entity_id,
        )
    except Exception as e:
        logger.error(f"Automation handler failed: {str(e)}")
    finally:
        db.close()


def register_automation_handler():
    """Register automation handler with event emitter."""
    from app.core.events.emitter import event_emitter
    event_emitter.register_handler(automation_event_handler)
    logger.info("Automation event handler registered")
