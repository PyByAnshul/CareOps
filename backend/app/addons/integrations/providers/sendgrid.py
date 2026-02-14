import logging
from typing import Any, Dict, List, Optional

from app.addons.integrations.providers.base import EmailProvider

logger = logging.getLogger(__name__)


class SendGridProvider(EmailProvider):
    """SendGrid email provider (mock implementation)."""
    
    def validate_config(self) -> bool:
        return "api_key" in self.config and "from_email" in self.config
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Send email via SendGrid (mock)."""
        try:
            if not self.validate_config():
                return {
                    "success": False,
                    "message": "Invalid SendGrid configuration",
                }
            
            # Mock implementation - would use sendgrid library in production
            logger.info(f"[MOCK SendGrid] Sending email to {to_email}")
            logger.info(f"[MOCK SendGrid] Subject: {subject}")
            logger.info(f"[MOCK SendGrid] Body: {body[:100]}...")
            
            # Simulate success
            return {
                "success": True,
                "message": f"Email sent to {to_email} via SendGrid (mock)",
            }
        
        except Exception as e:
            logger.error(f"Failed to send email via SendGrid: {str(e)}")
            return {
                "success": False,
                "message": str(e),
            }
