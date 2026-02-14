from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.addons.calendar.schemas import CalendarSettingsResponse, CalendarSettingsUpdate
from app.addons.calendar.service import CalendarService
from app.addons.users.models import User
from app.addons.workspace.models import Workspace
from app.core.db import get_db
from app.core.security.deps import get_current_workspace
from app.core.security.permissions import PermissionChecker

router = APIRouter(tags=["calendar"])


@router.get("/settings", response_model=CalendarSettingsResponse)
def get_settings(
    current_user: User = Depends(PermissionChecker("settings.read")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """Get calendar settings."""
    service = CalendarService(db, workspace.id)
    return service.get_or_create_settings()


@router.put("/settings", response_model=CalendarSettingsResponse)
def update_settings(
    data: CalendarSettingsUpdate,
    current_user: User = Depends(PermissionChecker("settings.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """Update calendar settings."""
    service = CalendarService(db, workspace.id)
    return service.update_settings(
        auto_send_invites=data.auto_send_invites,
        include_description=data.include_description,
        email_template=data.email_template,
    )


@router.post("/send-invite/{booking_id}")
def send_invite(
    booking_id: int,
    current_user: User = Depends(PermissionChecker("bookings.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """Manually send calendar invite for a booking."""
    service = CalendarService(db, workspace.id)
    result = service.send_calendar_invite(booking_id)
    return result
