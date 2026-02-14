import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.addons.integrations.models import Integration
from app.addons.integrations.providers.base import EmailProvider
from app.addons.integrations.providers.gmail import GmailProvider
from app.addons.integrations.providers.sendgrid import SendGridProvider
from app.addons.integrations.providers.smtp import SMTPProvider

logger = logging.getLogger(__name__)


class ProviderFactory:
    """Factory for creating email provider instances."""
    
    PROVIDERS = {
        "smtp": SMTPProvider,
        "sendgrid": SendGridProvider,
        "gmail": GmailProvider,
    }
    
    @classmethod
    def get_email_provider(cls, workspace_id: int, db: Session) -> Optional[EmailProvider]:
        """
        Get email provider for a workspace.
        
        Returns:
            EmailProvider instance or None if not configured.
        """
        integration = db.query(Integration).filter(
            Integration.workspace_id == workspace_id,
            Integration.integration_type == "email",
            Integration.is_active == True,
        ).first()
        
        if not integration:
            logger.warning(f"No active email integration for workspace {workspace_id}")
            return None
        
        provider_class = cls.PROVIDERS.get(integration.provider)
        if not provider_class:
            logger.error(f"Unknown email provider: {integration.provider}")
            return None
        
        try:
            provider = provider_class(integration.config)
            if not provider.validate_config():
                logger.error(f"Invalid configuration for provider {integration.provider}")
                return None
            
            return provider
        
        except Exception as e:
            logger.error(f"Failed to initialize provider: {str(e)}")
            return None
    
    @classmethod
    def create_provider(cls, provider_name: str, config: dict) -> Optional[EmailProvider]:
        """Create a provider instance directly (for testing)."""
        provider_class = cls.PROVIDERS.get(provider_name)
        if not provider_class:
            return None
        
        return provider_class(config)
