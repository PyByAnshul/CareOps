from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.types import TypeDecorator

from app.core.db import Base


class JSONType(TypeDecorator):
    """Platform-independent JSON type."""
    impl = Text
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            import json
            return json.dumps(value)
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            import json
            return json.loads(value)
        return value


class Form(Base):
    __tablename__ = "forms"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False)
    form_type = Column(String, nullable=False, default="booking")  # booking, inquiry, quote
    schema = Column(JSONType, nullable=False)  # Form field definitions
    is_active = Column(Boolean, default=True, nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)  # Public access token
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class FormSubmission(Base):
    __tablename__ = "form_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("forms.id"), nullable=False, index=True)
    booking_id = Column(Integer, nullable=True)
    inquiry_id = Column(Integer, nullable=True)
    contact_email = Column(String, nullable=False, index=True)
    answers = Column(JSONType, nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending, completed
    token = Column(String, unique=True, nullable=False, index=True)
    submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Inquiry(Base):
    __tablename__ = "inquiries"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, nullable=False, index=True)
    form_submission_id = Column(Integer, ForeignKey("form_submissions.id"), nullable=True)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False, index=True)
    inquiry_type = Column(String, nullable=False)  # inquiry, quote
    subject = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="new")  # new, contacted, converted, closed
    assigned_to = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
