from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.addons.permissions.schemas import PermissionResponse
from app.addons.permissions.service import PermissionService
from app.addons.users.models import User
from app.addons.users.schemas import Token, UserLogin, UserRegister, UserResponse
from app.addons.users.service import UserService
from app.core.db import get_db
from app.core.security.deps import get_current_workspace, require_active_user

router = APIRouter(tags=["users"])


def require_owner(current_user: User = Depends(require_active_user)) -> User:
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can manage user permissions",
        )
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.create_user(user_data)
    perm_service = PermissionService(db)
    if user.role == "owner":
        perm_service.assign_all_permissions(user.id)
    else:
        perm_service.assign_default_staff_permissions(user.id)
    return user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.authenticate_user(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    access_token = service.generate_token(user)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(require_active_user)):
    return current_user


@router.get("/me/permissions")
def get_my_permissions(
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    """Return current user's permission names. Owners get all permission names for UI."""
    service = PermissionService(db)
    if current_user.role == "owner":
        perms = service.list_permissions()
        return [p.name for p in perms]
    user_perms = service.list_user_permissions(current_user.id)
    return [p.name for p in user_perms]


@router.get("/dashboard")
def get_dashboard(current_user: User = Depends(require_active_user)):
    """Dashboard endpoint - returns basic user info and confirms authentication"""
    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "workspace_id": current_user.workspace_id,
        },
        "status": "authenticated"
    }


@router.get("/", response_model=List[UserResponse])
def list_workspace_users(
    current_user: User = Depends(require_active_user),
    workspace=Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """List all users in the current workspace (login access)."""
    return db.query(User).filter(User.workspace_id == workspace.id).all()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    """Get user detail (no password). User must be in same workspace."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/{user_id}/permissions", response_model=List[PermissionResponse])
def get_user_permissions(
    user_id: int,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    """List permissions assigned to a user. Owner only."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    service = PermissionService(db)
    return service.list_user_permissions(user_id)
