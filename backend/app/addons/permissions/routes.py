from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.addons.permissions.schemas import (
    AssignPermission,
    PermissionResponse,
    RemovePermission,
)
from app.addons.permissions.service import PermissionService
from app.addons.users.models import User
from app.core.db import get_db
from app.core.security.deps import require_active_user

router = APIRouter(tags=["permissions"])


def require_owner(current_user: User = Depends(require_active_user)) -> User:
    from fastapi import HTTPException
    
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can manage permissions",
        )
    return current_user


@router.get("/", response_model=List[PermissionResponse])
def list_permissions(
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    service = PermissionService(db)
    return service.list_permissions()


def _verify_user_workspace(user_id: int, current_user: User, db: Session) -> None:
    target = db.query(User).filter(User.id == user_id).first()
    if not target or target.workspace_id != current_user.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.post("/assign", status_code=status.HTTP_200_OK)
def assign_permission(
    data: AssignPermission,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    _verify_user_workspace(data.user_id, current_user, db)
    service = PermissionService(db)
    service.assign_permission(data.user_id, data.permission_name)
    return {"message": "Permission assigned successfully"}


@router.post("/remove", status_code=status.HTTP_200_OK)
def remove_permission(
    data: RemovePermission,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    _verify_user_workspace(data.user_id, current_user, db)
    service = PermissionService(db)
    service.remove_permission(data.user_id, data.permission_name)
    return {"message": "Permission removed successfully"}
