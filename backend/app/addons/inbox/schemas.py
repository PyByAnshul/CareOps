from datetime import datetime

from pydantic import BaseModel


class SendMessageRequest(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_type: str
    sender_id: int | None
    content: str
    direction: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: int
    workspace_id: int
    contact_email: str
    status: str
    automation_paused: bool
    last_message_at: datetime | None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    messages: list[MessageResponse] = []
