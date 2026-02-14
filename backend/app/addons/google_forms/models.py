from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
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


class GoogleFormIntegration(Base):
    __tablename__ = "google_form_integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False)
    google_form_id = Column(String, nullable=False)
    google_form_url = Column(String, nullable=False)
    webhook_secret = Column(String, nullable=False, unique=True, index=True)
    field_mappings = Column(JSONType, nullable=False)  # Maps Google Form fields to CareOps fields
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class GoogleFormSubmission(Base):
    __tablename__ = "google_form_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, nullable=False, index=True)
    booking_id = Column(Integer, nullable=True, index=True)
    raw_data = Column(JSONType, nullable=False)  # Original Google Form response
    mapped_data = Column(JSONType, nullable=False)  # Mapped to CareOps fields
    status = Column(String, nullable=False, default="pending")  # pending, processed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
