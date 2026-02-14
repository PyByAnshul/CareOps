from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.addons.contacts.schemas import (
    GrantPortalAccess,
    PartnerCreate,
    PartnerResponse,
    PartnerUpdate,
)
from app.addons.contacts.service import ContactService
from app.addons.users.models import User
from app.addons.workspace.models import Workspace
from app.core.db import get_db
from app.core.security.deps import get_current_workspace, require_active_user
from app.core.security.permissions import PermissionChecker

router = APIRouter(tags=["contacts"])


@router.get("/", response_model=List[PartnerResponse])
def list_partners(
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(PermissionChecker("contacts.read")),
    db: Session = Depends(get_db),
):
    service = ContactService(db)
    return service.list_partners(workspace.id)


@router.post("/", response_model=PartnerResponse, status_code=status.HTTP_201_CREATED)
def create_partner(
    data: PartnerCreate,
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(PermissionChecker("contacts.write")),
    db: Session = Depends(get_db),
):
    service = ContactService(db)
    return service.create_partner(data, workspace.id)


@router.get("/{partner_id}", response_model=PartnerResponse)
def get_partner(
    partner_id: int,
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(PermissionChecker("contacts.read")),
    db: Session = Depends(get_db),
):
    service = ContactService(db)
    return service.get_partner(partner_id, workspace.id)


@router.put("/{partner_id}", response_model=PartnerResponse)
def update_partner(
    partner_id: int,
    data: PartnerUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(PermissionChecker("contacts.write")),
    db: Session = Depends(get_db),
):
    service = ContactService(db)
    return service.update_partner(partner_id, data, workspace.id)


@router.post("/{partner_id}/grant-portal-access", response_model=PartnerResponse)
def grant_portal_access(
    partner_id: int,
    data: GrantPortalAccess,
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(PermissionChecker("contacts.write")),
    db: Session = Depends(get_db),
):
    service = ContactService(db)
    return service.grant_portal_access(
        partner_id, data.password, workspace.id, email=data.email
    )


@router.post("/{partner_id}/revoke-portal-access", response_model=PartnerResponse)
def revoke_portal_access(
    partner_id: int,
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(PermissionChecker("contacts.write")),
    db: Session = Depends(get_db),
):
    service = ContactService(db)
    return service.revoke_portal_access(partner_id, workspace.id)
