import requests
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.addons.webex.models import WebexMeeting
from app.addons.webex.schemas import WebexMeetingCreate
from app.addons.integrations.models import Integration


class WebexService:
    def __init__(self, db: Session, workspace_id: int):
        self.db = db
        self.workspace_id = workspace_id
        self.base_url = "https://webexapis.com/v1"
    
    def _get_access_token(self) -> Optional[str]:
        """Get Webex access token from integrations."""
        import logging
        logger = logging.getLogger(__name__)
        
        integration = self.db.query(Integration).filter(
            Integration.workspace_id == self.workspace_id,
            Integration.integration_type == "webex",
            Integration.is_active == True
        ).first()
        
        if not integration or not integration.config:
            logger.error("No Webex integration found")
            return None
        
        token = integration.config.get("access_token")
        if token:
            logger.info(f"Access token found, length: {len(token)}")
            logger.info(f"Token starts with: {token[:20]}...")
        else:
            logger.error(f"No access_token in config. Config keys: {list(integration.config.keys())}")
        
        return token
    
    def create_meeting(self, meeting_data: WebexMeetingCreate) -> WebexMeeting:
        """Create a Webex meeting."""
        import logging
        logger = logging.getLogger(__name__)
        
        access_token = self._get_access_token()
        
        if not access_token:
            logger.error("No Webex access token found")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Webex integration not configured. Please add your Webex access token in Settings > Integrations."
            )
        
        # Prepare meeting data for Webex API
        # Webex requires ISO 8601 format with timezone (e.g., 2024-01-15T14:30:00Z)
        start_time_str = meeting_data.start_time.strftime("%Y-%m-%dT%H:%M:%S")
        if not meeting_data.start_time.tzinfo:
            start_time_str += "Z"  # Add UTC timezone if not present
        
        webex_data = {
            "title": meeting_data.title,
            "start": start_time_str,
            "end": (meeting_data.start_time + timedelta(minutes=meeting_data.duration)).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            logger.info(f"Creating Webex meeting: {webex_data}")
            response = requests.post(
                f"{self.base_url}/meetings",
                json=webex_data,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"Webex API response status: {response.status_code}")
            logger.info(f"Webex API response: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            
            # Save meeting to database
            meeting = WebexMeeting(
                workspace_id=self.workspace_id,
                booking_id=meeting_data.booking_id,
                meeting_id=result["id"],
                meeting_number=result.get("meetingNumber"),
                meeting_link=result["webLink"],
                password=result.get("password"),
                host_key=result.get("hostKey"),
                title=meeting_data.title,
                start_time=meeting_data.start_time,
                duration=meeting_data.duration
            )
            
            self.db.add(meeting)
            self.db.commit()
            self.db.refresh(meeting)
            
            logger.info(f"Webex meeting created successfully: {meeting.meeting_link}")
            return meeting
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Webex API HTTP error: {e}")
            if e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
                try:
                    error_json = e.response.json()
                    error_msg = error_json.get('message', e.response.text)
                except:
                    error_msg = e.response.text
            else:
                error_msg = str(e)
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Webex API error: {error_msg}"
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Webex API request error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to connect to Webex: {str(e)}"
            )
    
    def get_all_meetings(self) -> list:
        """Get all Webex meetings for workspace."""
        return self.db.query(WebexMeeting).filter(
            WebexMeeting.workspace_id == self.workspace_id
        ).order_by(WebexMeeting.start_time.desc()).all()
    
    def get_meeting_by_booking(self, booking_id: int) -> Optional[WebexMeeting]:
        """Get Webex meeting for a booking."""
        return self.db.query(WebexMeeting).filter(
            WebexMeeting.workspace_id == self.workspace_id,
            WebexMeeting.booking_id == booking_id
        ).first()
    
    def delete_meeting(self, meeting_id: int) -> None:
        """Delete a Webex meeting."""
        meeting = self.db.query(WebexMeeting).filter(
            WebexMeeting.id == meeting_id,
            WebexMeeting.workspace_id == self.workspace_id
        ).first()
        
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found"
            )
        
        access_token = self._get_access_token()
        
        if access_token:
            headers = {"Authorization": f"Bearer {access_token}"}
            try:
                requests.delete(
                    f"{self.base_url}/meetings/{meeting.meeting_id}",
                    headers=headers
                )
            except:
                pass  # Continue even if API call fails
        
        self.db.delete(meeting)
        self.db.commit()
