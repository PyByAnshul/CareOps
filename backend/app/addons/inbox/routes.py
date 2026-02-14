from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.addons.inbox.schemas import (
    ConversationResponse,
    ConversationWithMessages,
    MessageResponse,
    SendMessageRequest,
)
from app.addons.inbox.models import Message
from app.addons.inbox.service import InboxService
from app.addons.inbox.tasks import send_outbound_message_task
from app.addons.users.models import User
from app.addons.workspace.models import Workspace
from app.core.db import get_db
from app.core.security.deps import get_current_workspace, require_active_user
from app.core.security.permissions import PermissionChecker

router = APIRouter(tags=["inbox"])


@router.get("/conversations", response_model=List[ConversationResponse])
def list_conversations(
    current_user: User = Depends(PermissionChecker("inbox.read")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = InboxService(db, workspace.id, current_user.id)
    return service.list_conversations()


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(PermissionChecker("inbox.read")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = InboxService(db, workspace.id, current_user.id)
    conversation = service.get_conversation(conversation_id)
    messages = service.get_messages(conversation_id)
    
    return ConversationWithMessages(
        id=conversation.id,
        workspace_id=conversation.workspace_id,
        contact_email=conversation.contact_email,
        status=conversation.status,
        automation_paused=conversation.automation_paused,
        last_message_at=conversation.last_message_at,
        created_at=conversation.created_at,
        messages=[MessageResponse.model_validate(msg) for msg in messages],
    )


@router.post("/sync-gmail", status_code=status.HTTP_200_OK)
def sync_gmail(
    current_user: User = Depends(PermissionChecker("inbox.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """Sync emails from Gmail to inbox."""
    from app.addons.integrations.providers.factory import ProviderFactory
    from app.addons.integrations.providers.gmail import GmailProvider
    
    # Get Gmail provider
    provider = ProviderFactory.get_email_provider(workspace.id, db)
    
    if not provider or not isinstance(provider, GmailProvider):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gmail integration not configured"
        )
    
    # Fetch emails
    emails = provider.fetch_emails(max_results=50)
    
    service = InboxService(db, workspace.id, current_user.id)
    synced_count = 0
    
    for email in emails:
        # Extract sender email
        from_email = email["from"]
        if "<" in from_email:
            from_email = from_email.split("<")[1].split(">")[0]
        
        # Find or create conversation
        conversation = service.find_or_create_conversation(from_email)
        
        # Check if message already exists (by checking recent messages)
        existing = db.query(Message).filter(
            Message.conversation_id == conversation.id,
            Message.content == email["body"][:500]  # Check first 500 chars
        ).first()
        
        if not existing:
            service.create_message(
                conversation_id=conversation.id,
                content=email["body"],
                sender_type="customer",
                direction="inbound",
            )
            synced_count += 1
    
    return {"success": True, "synced": synced_count, "total": len(emails)}


@router.post("/conversations/{conversation_id}/send", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: int,
    request: SendMessageRequest,
    current_user: User = Depends(PermissionChecker("inbox.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    from app.core.realtime.manager import connection_manager
    
    service = InboxService(db, workspace.id, current_user.id)
    
    # Create message
    message = service.create_message(
        conversation_id=conversation_id,
        content=request.content,
        sender_type="staff",
        direction="outbound",
        sender_id=current_user.id,
    )
    
    # Broadcast to workspace in real-time
    await connection_manager.broadcast_to_workspace(
        workspace.id,
        {
            "type": "message.created",
            "conversation_id": conversation_id,
            "message": MessageResponse.model_validate(message).model_dump(mode="json"),
        }
    )
    
    # Enqueue task to send email
    send_outbound_message_task.delay(message.id, workspace.id)
    
    return message
