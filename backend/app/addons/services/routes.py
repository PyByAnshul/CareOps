from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.addons.services.schemas import (
    AvailabilityCreate,
    AvailabilityResponse,
    ServiceCreate,
    ServiceResponse,
)
from app.addons.services.service import ServiceService
from app.addons.users.models import User
from app.addons.workspace.models import Workspace
from app.core.db import get_db
from app.core.security.deps import get_current_workspace, require_active_user
from app.core.security.permissions import PermissionChecker

router = APIRouter(tags=["services"])


@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    service_data: ServiceCreate,
    current_user: User = Depends(PermissionChecker("services.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = ServiceService(db, workspace.id)
    return service.create_service(service_data)


@router.get("/", response_model=List[ServiceResponse])
def list_services(
    current_user: User = Depends(PermissionChecker("services.read")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = ServiceService(db, workspace.id)
    return service.list_services()


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: int,
    current_user: User = Depends(PermissionChecker("services.read")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = ServiceService(db, workspace.id)
    return service.get_service(service_id)


@router.post("/{service_id}/availability", response_model=AvailabilityResponse, status_code=status.HTTP_201_CREATED)
def add_availability(
    service_id: int,
    availability_data: AvailabilityCreate,
    current_user: User = Depends(PermissionChecker("services.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = ServiceService(db, workspace.id)
    return service.add_availability(service_id, availability_data)


@router.get("/{service_id}/availability", response_model=List[AvailabilityResponse])
def list_availability(
    service_id: int,
    current_user: User = Depends(PermissionChecker("services.read")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = ServiceService(db, workspace.id)
    return service.list_availability(service_id)


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    service_data: ServiceCreate,
    current_user: User = Depends(PermissionChecker("services.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = ServiceService(db, workspace.id)
    return service.update_service(service_id, service_data)


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: int,
    current_user: User = Depends(PermissionChecker("services.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = ServiceService(db, workspace.id)
    service.delete_service(service_id)
