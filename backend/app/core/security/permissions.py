from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.addons.users.models import User
from app.core.db import get_db
from app.core.security.deps import require_active_user


class PermissionChecker:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission
    
    def __call__(
        self,
        current_user: User = Depends(require_active_user),
        db: Session = Depends(get_db),
    ) -> User:
        # Owners bypass all permission checks
        if current_user.role == "owner":
            return current_user
        
        # Staff must have explicit permission
        from app.addons.permissions.service import PermissionService
        
        service = PermissionService(db)
        has_permission = service.user_has_permission(current_user.id, self.required_permission)
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {self.required_permission}",
            )
        
        return current_user
