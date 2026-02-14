from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.addons.integrations.schemas import IntegrationCreate, IntegrationResponse, TestEmailRequest
from app.addons.integrations.service import IntegrationService
from app.addons.users.models import User
from app.addons.workspace.models import Workspace
from app.core.db import get_db
from app.core.security.deps import get_current_workspace, require_active_user
from app.core.security.permissions import PermissionChecker

router = APIRouter(tags=["integrations"])


@router.get("/", response_model=List[IntegrationResponse])
def list_integrations(
    current_user: User = Depends(PermissionChecker("settings.read")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = IntegrationService(db, workspace.id)
    return service.list_integrations()


@router.post("/", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
def create_integration(
    integration_data: IntegrationCreate,
    current_user: User = Depends(PermissionChecker("settings.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = IntegrationService(db, workspace.id)
    return service.create_integration(integration_data)


@router.put("/{integration_id}", response_model=IntegrationResponse)
def update_integration(
    integration_id: int,
    integration_data: IntegrationCreate,
    current_user: User = Depends(PermissionChecker("settings.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = IntegrationService(db, workspace.id)
    return service.update_integration(integration_id, integration_data)


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_integration(
    integration_id: int,
    current_user: User = Depends(PermissionChecker("settings.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = IntegrationService(db, workspace.id)
    service.delete_integration(integration_id)


@router.post("/email/test", status_code=status.HTTP_200_OK)
def test_email(
    request: TestEmailRequest,
    current_user: User = Depends(require_active_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = IntegrationService(db, workspace.id)
    result = service.send_test_email(request.to_email, request.subject, request.body)
    return {"message": "Test email sent successfully", "details": result}
