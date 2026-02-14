import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.addons.alerts.models import Alert

logger = logging.getLogger(__name__)


def create_alert(
    db: Session,
    workspace_id: int,
    alert_type: str,
    severity: str,
    title: str,
    message: str,
    link: Optional[str] = None,
    broadcast: bool = True,
) -> Alert:
    """
    Create an alert and optionally broadcast it via WebSocket.
    
    Args:
        db: Database session
        workspace_id: Workspace ID
        alert_type: Type of alert (automation_failed, email_failed, etc.)
        severity: Severity level (info, warning, critical)
        title: Alert title
        message: Alert message
        link: Optional link to related resource
        broadcast: Whether to broadcast via WebSocket
    
    Returns:
        Created Alert instance
    """
    alert = Alert(
        workspace_id=workspace_id,
        type=alert_type,
        severity=severity,
        title=title,
        message=message,
        link=link,
        is_dismissed=False,
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    logger.info(f"Alert created: {alert_type} - {title} (workspace {workspace_id})")
    
    # Broadcast to workspace if requested
    if broadcast:
        try:
            from app.core.realtime.manager import connection_manager
            import asyncio
            
            # Get or create event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Broadcast alert
            loop.run_until_complete(
                connection_manager.broadcast_to_workspace(
                    workspace_id,
                    {
                        "type": "alert.created",
                        "alert": {
                            "id": alert.id,
                            "type": alert_type,
                            "severity": severity,
                            "title": title,
                            "message": message,
                            "link": link,
                            "created_at": alert.created_at.isoformat(),
                        }
                    }
                )
            )
        except Exception as e:
            logger.error(f"Failed to broadcast alert: {str(e)}")
    
    return alert
