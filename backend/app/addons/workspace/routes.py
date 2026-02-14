from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.addons.users.models import User
from app.addons.workspace.models import Workspace
from app.addons.workspace.schemas import WorkspaceCreate, WorkspaceResponse
from app.addons.workspace.service import WorkspaceService
from app.core.db import get_db
from app.core.security.deps import require_active_user

router = APIRouter(tags=["workspace"])


def require_owner(current_user: User = Depends(require_active_user)) -> User:
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can perform this action",
        )
    return current_user


@router.post("/create", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    service = WorkspaceService(db)
    workspace = service.create_workspace(workspace_data)
    return workspace


@router.get("/me", response_model=WorkspaceResponse)
def get_current_workspace(
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    service = WorkspaceService(db)
    workspace = service.get_workspace_by_id(current_user.workspace_id)
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    
    if not workspace.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Workspace is inactive",
        )
    
    return workspace
