import base64
import logging
from typing import Any, Dict, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.addons.integrations.providers.base import EmailProvider

logger = logging.getLogger(__name__)


class GmailProvider(EmailProvider):
    """Gmail email provider using OAuth2."""
    
    def validate_config(self) -> bool:
        required = ["access_token", "refresh_token", "client_id", "client_secret"]
        return all(key in self.config for key in required)
    
    def _get_service(self):
        """Get Gmail API service."""
        creds = Credentials(
            token=self.config["access_token"],
            refresh_token=self.config["refresh_token"],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.config["client_id"],
            client_secret=self.config["client_secret"],
        )
        
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            self.config["access_token"] = creds.token
        
        return build("gmail", "v1", credentials=creds)
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False,
        attachments: Any = None,
    ) -> Dict[str, Any]:
        """Send email via Gmail API."""
        try:
            if not self.validate_config():
                return {"success": False, "message": "Invalid Gmail configuration"}
            
            service = self._get_service()
            
            from email.mime.text import MIMEText
            message = MIMEText(body, "html" if html else "plain")
            message["to"] = to_email
            message["subject"] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            service.users().messages().send(
                userId="me", body={"raw": raw}
            ).execute()
            
            logger.info(f"Email sent via Gmail to {to_email}")
            return {"success": True, "message": f"Email sent to {to_email}"}
        
        except Exception as e:
            logger.error(f"Failed to send email via Gmail: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def fetch_emails(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """Fetch emails from Gmail inbox."""
        try:
            if not self.validate_config():
                return []
            
            service = self._get_service()
            results = service.users().messages().list(
                userId="me", maxResults=max_results, labelIds=["INBOX"]
            ).execute()
            
            messages = results.get("messages", [])
            emails = []
            
            for msg in messages:
                msg_data = service.users().messages().get(
                    userId="me", id=msg["id"], format="full"
                ).execute()
                
                headers = {h["name"]: h["value"] for h in msg_data["payload"]["headers"]}
                
                # Extract body
                body = ""
                if "parts" in msg_data["payload"]:
                    for part in msg_data["payload"]["parts"]:
                        if part["mimeType"] == "text/plain":
                            body = base64.urlsafe_b64decode(
                                part["body"].get("data", "")
                            ).decode("utf-8")
                            break
                elif "body" in msg_data["payload"]:
                    body = base64.urlsafe_b64decode(
                        msg_data["payload"]["body"].get("data", "")
                    ).decode("utf-8")
                
                emails.append({
                    "id": msg["id"],
                    "thread_id": msg_data["threadId"],
                    "from": headers.get("From", ""),
                    "to": headers.get("To", ""),
                    "subject": headers.get("Subject", ""),
                    "date": headers.get("Date", ""),
                    "body": body,
                    "snippet": msg_data.get("snippet", ""),
                })
            
            return emails
        
        except Exception as e:
            logger.error(f"Failed to fetch emails from Gmail: {str(e)}")
            return []
