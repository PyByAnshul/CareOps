from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.addons.users.models import User
from app.core.db import get_db
from app.core.security.jwt import decode_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    print(f"Received token: {token[:20]}...")
    payload = decode_token(token)
    print(f"Decoded payload: {payload}")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    # Convert sub to int since it's stored as string in JWT
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID",
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


def require_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


def get_current_workspace(
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    from app.addons.workspace.models import Workspace
    
    print(f"Looking for workspace_id: {current_user.workspace_id}")
    workspace = db.query(Workspace).filter(Workspace.id == current_user.workspace_id).first()
    
    if not workspace:
        # Create default workspace if it doesn't exist
        workspace = Workspace(
            id=current_user.workspace_id,
            name="Default Workspace",
            is_active=True
        )
        db.add(workspace)
        db.commit()
        db.refresh(workspace)
        print(f"Created workspace: {workspace.id}")
    
    if not workspace.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Workspace is inactive",
        )
    
    return workspace


def verify_workspace_access(
    workspace_id: int,
    current_user: User = Depends(require_active_user),
) -> User:
    if current_user.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this workspace",
        )
    return current_user
