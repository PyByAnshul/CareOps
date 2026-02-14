from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.addons.inbox.models import Conversation, Message


class InboxService:
    def __init__(self, db: Session, workspace_id: int, user_id: int):
        self.db = db
        self.workspace_id = workspace_id
        self.user_id = user_id
    
    def list_conversations(self) -> List[Conversation]:
        """List all conversations for workspace."""
        return self.db.query(Conversation).filter(
            Conversation.workspace_id == self.workspace_id
        ).order_by(Conversation.last_message_at.desc()).all()
    
    def get_conversation(self, conversation_id: int) -> Conversation:
        """Get conversation with workspace check."""
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.workspace_id == self.workspace_id,
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
        
        return conversation
    
    def get_messages(self, conversation_id: int) -> List[Message]:
        """Get all messages for a conversation."""
        # Verify conversation belongs to workspace
        self.get_conversation(conversation_id)
        
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).all()
    
    def find_or_create_conversation(self, contact_email: str) -> Conversation:
        """Find existing conversation or create new one."""
        conversation = self.db.query(Conversation).filter(
            Conversation.workspace_id == self.workspace_id,
            Conversation.contact_email == contact_email,
            Conversation.status == "active",
        ).first()
        
        if not conversation:
            conversation = Conversation(
                workspace_id=self.workspace_id,
                contact_email=contact_email,
                status="active",
                automation_paused=False,
            )
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
        
        return conversation
    
    def create_message(
        self,
        conversation_id: int,
        content: str,
        sender_type: str,
        direction: str,
        sender_id: Optional[int] = None,
    ) -> Message:
        """Create a new message in conversation."""
        # Verify conversation
        conversation = self.get_conversation(conversation_id)
        
        message = Message(
            conversation_id=conversation_id,
            sender_type=sender_type,
            sender_id=sender_id,
            content=content,
            direction=direction,
            status="pending",
        )
        
        self.db.add(message)
        
        # Update conversation timestamp
        conversation.last_message_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def update_message_status(self, message_id: int, status: str) -> None:
        """Update message status."""
        message = self.db.query(Message).filter(Message.id == message_id).first()
        if message:
            message.status = status
            self.db.commit()
