from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.addons.dashboard.schemas import DashboardSummary
from app.addons.dashboard.service import DashboardService
from app.addons.users.models import User
from app.addons.workspace.models import Workspace
from app.core.db import get_db
from app.core.security.deps import get_current_workspace, require_active_user

router = APIRouter(tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    current_user: User = Depends(require_active_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    print(f"Dashboard summary called for user {current_user.id}")
    service = DashboardService(db, workspace.id)
    return service.get_summary()


@router.get("/booking-stats")
def get_booking_stats(
    current_user: User = Depends(require_active_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = DashboardService(db, workspace.id)
    return service.get_booking_stats()


@router.get("/inventory-stats")
def get_inventory_stats(
    current_user: User = Depends(require_active_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = DashboardService(db, workspace.id)
    return service.get_inventory_stats()
