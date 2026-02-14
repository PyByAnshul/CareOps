from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text

from app.core.db import Base


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, nullable=False, index=True)
    contact_email = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="active")  # active/archived
    automation_paused = Column(Boolean, default=False, nullable=False)
    last_message_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    sender_type = Column(String, nullable=False)  # staff/customer/system
    sender_id = Column(Integer, nullable=True)  # user_id if staff
    content = Column(Text, nullable=False)
    direction = Column(String, nullable=False)  # inbound/outbound
    status = Column(String, nullable=False, default="pending")  # pending/sent/failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
