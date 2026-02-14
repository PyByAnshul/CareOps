import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Any, Dict, List, Optional

from app.addons.integrations.providers.base import EmailProvider

logger = logging.getLogger(__name__)


class SMTPProvider(EmailProvider):
    """SMTP email provider."""
    
    def validate_config(self) -> bool:
        required = ["host", "port", "username", "password", "from_email"]
        return all(key in self.config for key in required)
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Send email via SMTP."""
        try:
            if not self.validate_config():
                return {
                    "success": False,
                    "message": "Invalid SMTP configuration",
                }
            
            has_attachments = attachments and len(attachments) > 0
            if has_attachments:
                msg = MIMEMultipart("mixed")
            else:
                msg = MIMEMultipart("alternative")
            
            msg["From"] = self.config["from_email"]
            msg["To"] = to_email
            msg["Subject"] = subject
            
            if has_attachments:
                body_part = MIMEMultipart("alternative")
                body_part.attach(MIMEText(body, "html" if html else "plain"))
                msg.attach(body_part)
            else:
                if html:
                    msg.attach(MIMEText(body, "html"))
                else:
                    msg.attach(MIMEText(body, "plain"))
            
            if attachments:
                for att in attachments:
                    filename = att.get("filename", "attachment")
                    content = att.get("content", "")
                    content_type = att.get("content_type", "application/octet-stream")
                    if isinstance(content, str):
                        content = content.encode("utf-8")
                    main_type, sub_type = content_type.split("/", 1) if "/" in content_type else ("application", "octet-stream")
                    part = MIMEBase(main_type, sub_type)
                    part.set_payload(content)
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", "attachment", filename=filename)
                    msg.attach(part)
            
            # Connect to SMTP server
            use_tls = self.config.get("use_tls", True)
            
            if use_tls:
                server = smtplib.SMTP(self.config["host"], self.config["port"])
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.config["host"], self.config["port"])
            
            server.login(self.config["username"], self.config["password"])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            
            return {
                "success": True,
                "message": f"Email sent to {to_email}",
            }
        
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return {
                "success": False,
                "message": str(e),
            }
