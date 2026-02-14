import logging
from typing import Any, Dict

from app.core.db import SessionLocal
from app.core.jobs.base_tasks import BaseTask
from app.core.jobs.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(base=BaseTask, bind=True, max_retries=3)
def send_outbound_message_task(self, message_id: int, workspace_id: int) -> Dict[str, Any]:
    """
    Send outbound message via email provider.
    """
    from app.addons.inbox.models import Conversation, Message
    from app.addons.integrations.providers.factory import ProviderFactory
    import asyncio
    
    db = SessionLocal()
    try:
        # Get message
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            logger.error(f"Message {message_id} not found")
            return {"success": False, "message": "Message not found"}
        
        # Get conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == message.conversation_id
        ).first()
        
        if not conversation:
            logger.error(f"Conversation {message.conversation_id} not found")
            message.status = "failed"
            db.commit()
            _broadcast_status_update(workspace_id, message)
            return {"success": False, "message": "Conversation not found"}
        
        # Get email provider
        provider = ProviderFactory.get_email_provider(workspace_id, db)
        
        if not provider:
            logger.warning(f"No email provider configured for workspace {workspace_id}")
            message.status = "failed"
            db.commit()
            _broadcast_status_update(workspace_id, message)
            return {"success": False, "message": "No email provider configured"}
        
        # Send email
        subject = f"Message from CareOps"
        email_result = provider.send_email(
            conversation.contact_email,
            subject,
            message.content
        )
        
        # Update message status
        if email_result["success"]:
            message.status = "sent"
            logger.info(f"Message {message_id} sent to {conversation.contact_email}")
        else:
            message.status = "failed"
            logger.error(f"Failed to send message {message_id}: {email_result['message']}")
        
        db.commit()
        db.refresh(message)
        
        # Broadcast status update
        _broadcast_status_update(workspace_id, message)
        
        return email_result
    
    except Exception as e:
        logger.error(f"send_outbound_message_task failed: {str(e)}")
        
        # Update message status to failed
        try:
            message = db.query(Message).filter(Message.id == message_id).first()
            if message:
                message.status = "failed"
                db.commit()
                _broadcast_status_update(workspace_id, message)
        except:
            pass
        
        raise
    finally:
        db.close()


def _broadcast_status_update(workspace_id: int, message) -> None:
    """Broadcast message status update to workspace."""
    try:
        from app.core.realtime.manager import connection_manager
        import asyncio
        
        # Create event loop if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Broadcast update
        loop.run_until_complete(
            connection_manager.broadcast_to_workspace(
                workspace_id,
                {
                    "type": "message.status_updated",
                    "message_id": message.id,
                    "conversation_id": message.conversation_id,
                    "status": message.status,
                }
            )
        )
    except Exception as e:
        logger.error(f"Failed to broadcast status update: {str(e)}")
