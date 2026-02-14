from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.addons.services.models import Service, ServiceAvailability
from app.addons.services.schemas import AvailabilityCreate, ServiceCreate


class ServiceService:
    def __init__(self, db: Session, workspace_id: int):
        self.db = db
        self.workspace_id = workspace_id
    
    def create_service(self, service_data: ServiceCreate) -> Service:
        """Create a new service."""
        service = Service(
            workspace_id=self.workspace_id,
            name=service_data.name,
            duration_minutes=service_data.duration_minutes,
            is_active=True,
        )
        
        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)
        
        return service
    
    def list_services(self) -> List[Service]:
        """List all services for workspace."""
        return self.db.query(Service).filter(
            Service.workspace_id == self.workspace_id
        ).order_by(Service.name).all()
    
    def get_service(self, service_id: int) -> Service:
        """Get service by ID with workspace check."""
        service = self.db.query(Service).filter(
            Service.id == service_id,
            Service.workspace_id == self.workspace_id,
        ).first()
        
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found",
            )
        
        return service
    
    def add_availability(self, service_id: int, availability_data: AvailabilityCreate) -> ServiceAvailability:
        """Add availability window to service."""
        # Verify service exists and belongs to workspace
        self.get_service(service_id)
        
        availability = ServiceAvailability(
            service_id=service_id,
            day_of_week=availability_data.day_of_week,
            start_time=availability_data.start_time,
            end_time=availability_data.end_time,
        )
        
        self.db.add(availability)
        self.db.commit()
        self.db.refresh(availability)
        
        return availability
    
    def list_availability(self, service_id: int) -> List[ServiceAvailability]:
        """List availability windows for service."""
        # Verify service exists and belongs to workspace
        self.get_service(service_id)
        
        return self.db.query(ServiceAvailability).filter(
            ServiceAvailability.service_id == service_id
        ).order_by(ServiceAvailability.day_of_week, ServiceAvailability.start_time).all()

    
    def update_service(self, service_id: int, service_data: ServiceCreate) -> Service:
        """Update an existing service."""
        service = self.get_service(service_id)
        
        service.name = service_data.name
        service.duration_minutes = service_data.duration_minutes
        
        self.db.commit()
        self.db.refresh(service)
        
        return service
    
    def delete_service(self, service_id: int) -> None:
        """Delete a service."""
        service = self.get_service(service_id)
        
        self.db.delete(service)
        self.db.commit()
