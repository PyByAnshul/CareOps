from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.addons.automation.schemas import AutomationEventLogResponse
from app.addons.automation.service import AutomationService
from app.addons.users.models import User
from app.addons.workspace.models import Workspace
from app.core.db import get_db
from app.core.security.deps import get_current_workspace, require_active_user

router = APIRouter(tags=["automation"])


@router.get("/logs", response_model=List[AutomationEventLogResponse])
def get_automation_logs(
    current_user: User = Depends(require_active_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = AutomationService(db, workspace.id)
    return service.get_logs()
