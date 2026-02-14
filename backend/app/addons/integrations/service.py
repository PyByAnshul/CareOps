from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.addons.integrations.models import Integration
from app.addons.integrations.providers.factory import ProviderFactory
from app.addons.integrations.schemas import IntegrationCreate


class IntegrationService:
    def __init__(self, db: Session, workspace_id: int):
        self.db = db
        self.workspace_id = workspace_id
    
    def create_integration(self, data: IntegrationCreate) -> Integration:
        """Create a new integration for the workspace."""
        # Deactivate existing integrations of same type
        existing = self.db.query(Integration).filter(
            Integration.workspace_id == self.workspace_id,
            Integration.integration_type == data.integration_type,
        ).all()
        
        for integration in existing:
            integration.is_active = False
        
        # Create new integration
        integration = Integration(
            workspace_id=self.workspace_id,
            integration_type=data.integration_type,
            provider=data.provider,
            config=data.config,
            is_active=True,
        )
        
        self.db.add(integration)
        self.db.commit()
        self.db.refresh(integration)
        
        return integration
    
    def get_active_integration(self, integration_type: str) -> Optional[Integration]:
        """Get active integration for workspace."""
        return self.db.query(Integration).filter(
            Integration.workspace_id == self.workspace_id,
            Integration.integration_type == integration_type,
            Integration.is_active == True,
        ).first()
    
    def send_test_email(self, to_email: str, subject: str, body: str) -> dict:
        """Send a test email using workspace email provider."""
        provider = ProviderFactory.get_email_provider(self.workspace_id, self.db)
        
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active email integration configured",
            )
        
        result = provider.send_email(to_email, subject, body)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send email: {result['message']}",
            )
        
        return result

    
    def list_integrations(self):
        """List all integrations for workspace."""
        return self.db.query(Integration).filter(
            Integration.workspace_id == self.workspace_id
        ).all()
    
    def update_integration(self, integration_id: int, data: IntegrationCreate) -> Integration:
        """Update an existing integration."""
        integration = self.db.query(Integration).filter(
            Integration.id == integration_id,
            Integration.workspace_id == self.workspace_id,
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found",
            )
        
        integration.integration_type = data.integration_type
        integration.provider = data.provider
        integration.config = data.config
        
        self.db.commit()
        self.db.refresh(integration)
        
        return integration
    
    def delete_integration(self, integration_id: int):
        """Delete an integration."""
        integration = self.db.query(Integration).filter(
            Integration.id == integration_id,
            Integration.workspace_id == self.workspace_id,
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found",
            )
        
        self.db.delete(integration)
        self.db.commit()
