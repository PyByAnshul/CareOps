from sqlalchemy import Boolean, Column, Integer, String, Text
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


class Integration(Base):
    __tablename__ = "integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, nullable=False, index=True)
    integration_type = Column(String, nullable=False)  # email, sms, etc.
    provider = Column(String, nullable=False)  # smtp, sendgrid, etc.
    config = Column(JSONType, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
