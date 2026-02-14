from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.addons.forms.schemas import (
    FormCreate,
    FormResponse,
    FormSubmissionCreate,
    FormSubmissionResponse,
    PublicFormResponse,
)
from app.addons.forms.service import FormService
from app.addons.forms.tasks import send_form_email_task
from app.addons.users.models import User
from app.addons.workspace.models import Workspace
from app.core.db import get_db
from app.core.security.deps import get_current_workspace, require_active_user
from app.core.security.permissions import PermissionChecker

router = APIRouter(tags=["forms"])


@router.post("/", response_model=FormResponse, status_code=status.HTTP_201_CREATED)
def create_form(
    form_data: FormCreate,
    current_user: User = Depends(PermissionChecker("forms.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = FormService(db, workspace.id)
    return service.create_form(form_data)


@router.get("/", response_model=List[FormResponse])
def list_forms(
    current_user: User = Depends(PermissionChecker("forms.read")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = FormService(db, workspace.id)
    return service.list_forms()


@router.get("/{form_id}", response_model=FormResponse)
def get_form(
    form_id: int,
    current_user: User = Depends(PermissionChecker("forms.read")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = FormService(db, workspace.id)
    return service.get_form(form_id)


@router.get("/{form_id}/submissions", response_model=List[FormSubmissionResponse])
def list_submissions(
    form_id: int,
    current_user: User = Depends(PermissionChecker("forms.read")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = FormService(db, workspace.id)
    return service.list_submissions(form_id)


@router.get("/inquiries/list", response_model=List['InquiryResponse'])
def list_inquiries(
    status: str | None = None,
    current_user: User = Depends(PermissionChecker("forms.read")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    from app.addons.forms.schemas import InquiryResponse
    service = FormService(db, workspace.id)
    return service.list_inquiries(status)


@router.put("/inquiries/{inquiry_id}", response_model='InquiryResponse')
def update_inquiry(
    inquiry_id: int,
    status: str | None = None,
    assigned_to: int | None = None,
    current_user: User = Depends(PermissionChecker("forms.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    from app.addons.forms.schemas import InquiryResponse
    service = FormService(db, workspace.id)
    return service.update_inquiry(inquiry_id, status, assigned_to)


@router.put("/{form_id}", response_model=FormResponse)
def update_form(
    form_id: int,
    form_data: FormCreate,
    current_user: User = Depends(PermissionChecker("forms.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = FormService(db, workspace.id)
    return service.update_form(form_id, form_data)
