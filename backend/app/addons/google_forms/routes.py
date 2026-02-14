from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.addons.google_forms.schemas import (
    GoogleFormIntegrationCreate,
    GoogleFormIntegrationResponse,
    GoogleFormIntegrationUpdate,
    GoogleFormSubmissionResponse,
)
from app.addons.google_forms.service import GoogleFormService
from app.addons.users.models import User
from app.addons.workspace.models import Workspace
from app.core.db import get_db
from app.core.security.deps import get_current_workspace
from app.core.security.permissions import PermissionChecker

router = APIRouter(tags=["google-forms"])


@router.post("/", response_model=GoogleFormIntegrationResponse, status_code=status.HTTP_201_CREATED)
def create_integration(
    data: GoogleFormIntegrationCreate,
    current_user: User = Depends(PermissionChecker("integrations.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """Create a new Google Form integration."""
    service = GoogleFormService(db, workspace.id)
    return service.create_integration(data)


@router.get("/", response_model=List[GoogleFormIntegrationResponse])
def list_integrations(
    current_user: User = Depends(PermissionChecker("integrations.read")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """List all Google Form integrations."""
    service = GoogleFormService(db, workspace.id)
    return service.list_integrations()


@router.get("/{integration_id}", response_model=GoogleFormIntegrationResponse)
def get_integration(
    integration_id: int,
    current_user: User = Depends(PermissionChecker("integrations.read")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """Get integration by ID."""
    service = GoogleFormService(db, workspace.id)
    return service.get_integration(integration_id)


@router.put("/{integration_id}", response_model=GoogleFormIntegrationResponse)
def update_integration(
    integration_id: int,
    data: GoogleFormIntegrationUpdate,
    current_user: User = Depends(PermissionChecker("integrations.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """Update integration."""
    service = GoogleFormService(db, workspace.id)
    return service.update_integration(integration_id, data)


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_integration(
    integration_id: int,
    current_user: User = Depends(PermissionChecker("integrations.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """Delete integration."""
    service = GoogleFormService(db, workspace.id)
    service.delete_integration(integration_id)


@router.get("/{integration_id}/submissions", response_model=List[GoogleFormSubmissionResponse])
def list_submissions(
    integration_id: int,
    current_user: User = Depends(PermissionChecker("integrations.read")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """List submissions for an integration."""
    service = GoogleFormService(db, workspace.id)
    return service.list_submissions(integration_id)
