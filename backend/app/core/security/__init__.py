"""
Core security module for authentication and authorization.
"""

from app.core.security.deps import (
    get_current_user,
    get_current_workspace,
    require_active_user,
    verify_workspace_access,
)
from app.core.security.hashing import hash_password, verify_password
from app.core.security.jwt import create_access_token, decode_token
from app.core.security.permissions import PermissionChecker

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_token",
    "get_current_user",
    "require_active_user",
    "get_current_workspace",
    "verify_workspace_access",
    "PermissionChecker",
]
