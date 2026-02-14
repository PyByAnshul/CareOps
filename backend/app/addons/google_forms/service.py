import secrets
from datetime import date, datetime, time
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.addons.bookings.models import Booking
from app.addons.google_forms.models import GoogleFormIntegration, GoogleFormSubmission
from app.addons.google_forms.schemas import GoogleFormIntegrationCreate, GoogleFormIntegrationUpdate
from app.addons.services.models import Service


class GoogleFormService:
    def __init__(self, db: Session, workspace_id: int):
        self.db = db
        self.workspace_id = workspace_id
    
    def create_integration(self, data: GoogleFormIntegrationCreate) -> GoogleFormIntegration:
        """Create a new Google Form integration with field mappings."""
        webhook_secret = secrets.token_urlsafe(32)
        
        integration = GoogleFormIntegration(
            workspace_id=self.workspace_id,
            name=data.name,
            google_form_id=data.google_form_id,
            google_form_url=data.google_form_url,
            webhook_secret=webhook_secret,
            field_mappings=data.field_mappings,
            is_active=True,
        )
        
        self.db.add(integration)
        self.db.commit()
        self.db.refresh(integration)
        
        return integration
    
    def list_integrations(self) -> List[GoogleFormIntegration]:
        """List all Google Form integrations for workspace."""
        return self.db.query(GoogleFormIntegration).filter(
            GoogleFormIntegration.workspace_id == self.workspace_id
        ).order_by(GoogleFormIntegration.created_at.desc()).all()
    
    def get_integration(self, integration_id: int) -> GoogleFormIntegration:
        """Get integration by ID."""
        integration = self.db.query(GoogleFormIntegration).filter(
            GoogleFormIntegration.id == integration_id,
            GoogleFormIntegration.workspace_id == self.workspace_id,
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )
        
        return integration
    
    def update_integration(self, integration_id: int, data: GoogleFormIntegrationUpdate) -> GoogleFormIntegration:
        """Update integration."""
        integration = self.get_integration(integration_id)
        
        if data.name is not None:
            integration.name = data.name
        if data.google_form_url is not None:
            integration.google_form_url = data.google_form_url
        if data.field_mappings is not None:
            integration.field_mappings = data.field_mappings
        if data.is_active is not None:
            integration.is_active = data.is_active
        
        self.db.commit()
        self.db.refresh(integration)
        
        return integration
    
    def delete_integration(self, integration_id: int) -> None:
        """Delete integration."""
        integration = self.get_integration(integration_id)
        self.db.delete(integration)
        self.db.commit()
    
    def process_webhook(self, webhook_secret: str, email: str, responses: Dict[str, Any]) -> GoogleFormSubmission:
        """Process incoming webhook from Google Forms."""
        # Find integration by webhook secret
        integration = self.db.query(GoogleFormIntegration).filter(
            GoogleFormIntegration.webhook_secret == webhook_secret,
            GoogleFormIntegration.is_active == True,
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found or inactive"
            )
        
        # Map fields
        mapped_data = self._map_fields(integration.field_mappings, responses, email)
        
        # Create submission record
        submission = GoogleFormSubmission(
            integration_id=integration.id,
            raw_data={"email": email, "responses": responses},
            mapped_data=mapped_data,
            status="pending",
        )
        
        self.db.add(submission)
        self.db.flush()
        
        # Try to create booking
        try:
            booking = self._create_booking(integration.workspace_id, mapped_data)
            submission.booking_id = booking.id
            submission.status = "processed"
        except Exception as e:
            submission.status = "failed"
            submission.error_message = str(e)
        
        self.db.commit()
        self.db.refresh(submission)
        
        return submission
    
    def _map_fields(self, field_mappings: Dict[str, str], responses: Dict[str, Any], email: str) -> Dict[str, Any]:
        """Map Google Form fields to CareOps fields."""
        mapped = {"customer_email": email}
        
        for google_field, careops_field in field_mappings.items():
            if google_field in responses:
                mapped[careops_field] = responses[google_field]
        
        return mapped
    
    def _create_booking(self, workspace_id: int, mapped_data: Dict[str, Any]) -> Booking:
        """Create booking from mapped data."""
        # Parse service (by name or ID)
        service_id = None
        if "service_name" in mapped_data:
            service = self.db.query(Service).filter(
                Service.workspace_id == workspace_id,
                Service.name.ilike(f"%{mapped_data['service_name']}%")
            ).first()
            if service:
                service_id = service.id
        elif "service_id" in mapped_data:
            service_id = int(mapped_data["service_id"])
        
        # Parse date
        booking_date = date.today()
        if "booking_date" in mapped_data:
            try:
                booking_date = date.fromisoformat(str(mapped_data["booking_date"]))
            except (ValueError, TypeError):
                pass
        
        # Parse time
        booking_time = time(9, 0)
        if "booking_time" in mapped_data:
            try:
                time_str = str(mapped_data["booking_time"])
                parts = time_str.split(":")
                booking_time = time(int(parts[0]), int(parts[1]))
            except (ValueError, TypeError, IndexError):
                pass
        
        # Create booking
        booking = Booking(
            workspace_id=workspace_id,
            service_id=service_id,
            customer_name=mapped_data.get("customer_name", "Unknown"),
            customer_email=mapped_data.get("customer_email", ""),
            booking_date=booking_date,
            booking_time=booking_time,
            status="pending",
            notes=mapped_data.get("notes"),
            created_by=1,  # System user
        )
        
        self.db.add(booking)
        self.db.flush()
        
        return booking
    
    def list_submissions(self, integration_id: Optional[int] = None) -> List[GoogleFormSubmission]:
        """List submissions."""
        query = self.db.query(GoogleFormSubmission).join(GoogleFormIntegration).filter(
            GoogleFormIntegration.workspace_id == self.workspace_id
        )
        
        if integration_id:
            query = query.filter(GoogleFormSubmission.integration_id == integration_id)
        
        return query.order_by(GoogleFormSubmission.created_at.desc()).all()
