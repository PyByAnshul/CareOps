import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class EventEmitter:
    def __init__(self):
        self.handlers = []
    
    def register_handler(self, handler):
        """Register an event handler."""
        self.handlers.append(handler)
    
    def emit(self, event_name: str, data: Dict[str, Any]) -> None:
        """
        Emit an event with data.
        Calls all registered handlers.
        """
        logger.info(f"Event emitted: {event_name}", extra={"event_data": data})
        
        for handler in self.handlers:
            try:
                handler(event_name, data)
            except Exception as e:
                logger.error(f"Event handler failed: {str(e)}")


event_emitter = EventEmitter()
