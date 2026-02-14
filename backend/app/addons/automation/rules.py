from typing import Any, Dict, List

import logging

logger = logging.getLogger(__name__)


class AutomationAction:
    """Base class for automation actions."""
    
    def __init__(self, name: str):
        self.name = name
    
    def execute(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the action and return result."""
        raise NotImplementedError


class SendConfirmationAction(AutomationAction):
    """Mock action: send booking confirmation."""
    
    def __init__(self):
        super().__init__("send_confirmation")
    
    def execute(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[MOCK] Sending confirmation email to {event_data.get('customer_email')}")
        return {
            "action": self.name,
            "status": "success",
            "message": f"Confirmation would be sent to {event_data.get('customer_email')}",
        }


class NotifyStaffAction(AutomationAction):
    """Mock action: notify staff about new booking."""
    
    def __init__(self):
        super().__init__("notify_staff")
    
    def execute(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[MOCK] Notifying staff about booking {event_data.get('booking_id')}")
        return {
            "action": self.name,
            "status": "success",
            "message": f"Staff would be notified about booking {event_data.get('booking_id')}",
        }


class DeductInventoryAction(AutomationAction):
    """Mock action: deduct inventory."""
    
    def __init__(self):
        super().__init__("deduct_inventory")
    
    def execute(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[MOCK] Deducting inventory for booking {event_data.get('booking_id')}")
        return {
            "action": self.name,
            "status": "success",
            "message": "Inventory would be deducted",
        }


# Rule definitions: event_type -> list of actions
AUTOMATION_RULES = {
    "booking.created": [
        SendConfirmationAction(),
        NotifyStaffAction(),
    ],
    "booking.confirmed": [
        SendConfirmationAction(),
    ],
    "booking.cancelled": [
        NotifyStaffAction(),
    ],
}


def get_actions_for_event(event_type: str) -> List[AutomationAction]:
    """Get list of actions for a given event type."""
    return AUTOMATION_RULES.get(event_type, [])
