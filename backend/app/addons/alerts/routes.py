from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.addons.alerts.schemas import AlertResponse
from app.addons.alerts.service import AlertService
from app.addons.users.models import User
from app.addons.workspace.models import Workspace
from app.core.db import get_db
from app.core.security.deps import get_current_workspace, require_active_user

router = APIRouter(tags=["alerts"])


@router.get("/", response_model=List[AlertResponse])
def list_alerts(
    current_user: User = Depends(require_active_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = AlertService(db, workspace.id)
    return service.list_alerts()


@router.post("/{alert_id}/dismiss", response_model=AlertResponse)
def dismiss_alert(
    alert_id: int,
    current_user: User = Depends(require_active_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = AlertService(db, workspace.id)
    return service.dismiss_alert(alert_id)
