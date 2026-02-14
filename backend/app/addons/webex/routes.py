from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.addons.webex.schemas import WebexMeetingCreate, WebexMeetingResponse
from app.addons.webex.service import WebexService
from app.addons.users.models import User
from app.addons.workspace.models import Workspace
from app.core.db import get_db
from app.core.security.deps import get_current_workspace, require_active_user

router = APIRouter(tags=["webex"])


@router.get("/meetings", response_model=List[WebexMeetingResponse])
def list_webex_meetings(
    current_user: User = Depends(require_active_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = WebexService(db, workspace.id)
    return service.get_all_meetings()


@router.post("/meetings", response_model=WebexMeetingResponse)
def create_webex_meeting(
    meeting_data: WebexMeetingCreate,
    current_user: User = Depends(require_active_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = WebexService(db, workspace.id)
    return service.create_meeting(meeting_data)


@router.get("/meetings/booking/{booking_id}", response_model=WebexMeetingResponse)
def get_meeting_by_booking(
    booking_id: int,
    current_user: User = Depends(require_active_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = WebexService(db, workspace.id)
    meeting = service.get_meeting_by_booking(booking_id)
    if not meeting:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    return meeting


@router.delete("/meetings/{meeting_id}")
def delete_webex_meeting(
    meeting_id: int,
    current_user: User = Depends(require_active_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = WebexService(db, workspace.id)
    service.delete_meeting(meeting_id)
    return {"message": "Meeting deleted successfully"}
