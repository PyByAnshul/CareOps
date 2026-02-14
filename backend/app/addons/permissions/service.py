from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.addons.permissions.models import Permission, UserPermission
from app.addons.users.models import User

SEED_PERMISSIONS = [
    {"name": "inbox.read", "description": "Read inbox messages", "module": "inbox"},
    {"name": "inbox.write", "description": "Write inbox messages", "module": "inbox"},
    {"name": "bookings.read", "description": "Read bookings", "module": "bookings"},
    {"name": "bookings.write", "description": "Write bookings", "module": "bookings"},
    {"name": "bookings.delete", "description": "Delete bookings", "module": "bookings"},
    {"name": "forms.read", "description": "Read forms", "module": "forms"},
    {"name": "forms.write", "description": "Write forms", "module": "forms"},
    {"name": "forms.delete", "description": "Delete forms", "module": "forms"},
    {"name": "services.read", "description": "Read services", "module": "services"},
    {"name": "services.write", "description": "Write services", "module": "services"},
    {"name": "services.delete", "description": "Delete services", "module": "services"},
    {"name": "inventory.read", "description": "Read inventory", "module": "inventory"},
    {"name": "inventory.write", "description": "Write inventory", "module": "inventory"},
    {"name": "inventory.delete", "description": "Delete inventory", "module": "inventory"},
    {"name": "contacts.read", "description": "Read contacts", "module": "contacts"},
    {"name": "contacts.write", "description": "Write contacts", "module": "contacts"},
    {"name": "contacts.delete", "description": "Delete contacts", "module": "contacts"},
    {"name": "google_forms.read", "description": "Read Google Forms", "module": "google_forms"},
    {"name": "google_forms.write", "description": "Write Google Forms", "module": "google_forms"},
    {"name": "google_forms.delete", "description": "Delete Google Forms", "module": "google_forms"},
]


class PermissionService:
    def __init__(self, db: Session):
        self.db = db
    
    def seed_permissions(self) -> None:
        for perm_data in SEED_PERMISSIONS:
            existing = self.db.query(Permission).filter(Permission.name == perm_data["name"]).first()
            if not existing:
                permission = Permission(**perm_data)
                self.db.add(permission)
        self.db.commit()
    
    def list_permissions(self) -> List[Permission]:
        return self.db.query(Permission).all()

    def list_user_permissions(self, user_id: int) -> List[Permission]:
        """Return all permissions assigned to a user."""
        return (
            self.db.query(Permission)
            .join(UserPermission, UserPermission.permission_id == Permission.id)
            .filter(UserPermission.user_id == user_id)
            .all()
        )

    def list_read_permission_names(self) -> List[str]:
        """Return permission names that are read-only (module.read)."""
        perms = self.db.query(Permission).filter(Permission.name.like("%.read")).all()
        return [p.name for p in perms]

    def list_non_delete_permission_names(self) -> List[str]:
        """Return permission names that are NOT delete (i.e. read and write only)."""
        perms = self.db.query(Permission).filter(~Permission.name.like("%.delete")).all()
        return [p.name for p in perms]

    def assign_all_permissions(self, user_id: int) -> None:
        """Assign every permission to the user (e.g. for owner/admin)."""
        perms = self.db.query(Permission).all()
        for perm in perms:
            existing = (
                self.db.query(UserPermission)
                .filter(
                    UserPermission.user_id == user_id,
                    UserPermission.permission_id == perm.id,
                )
                .first()
            )
            if not existing:
                self.db.add(UserPermission(user_id=user_id, permission_id=perm.id))
        self.db.commit()

    def assign_default_staff_permissions(self, user_id: int) -> None:
        """
        Assign read + write (create/update) for all modules to a new staff user.
        Does NOT assign any *.delete permissions.
        """
        names = self.list_non_delete_permission_names()
        for name in names:
            perm = self.db.query(Permission).filter(Permission.name == name).first()
            if not perm:
                continue
            existing = (
                self.db.query(UserPermission)
                .filter(
                    UserPermission.user_id == user_id,
                    UserPermission.permission_id == perm.id,
                )
                .first()
            )
            if not existing:
                self.db.add(UserPermission(user_id=user_id, permission_id=perm.id))
        self.db.commit()

    def assign_all_read_permissions(self, user_id: int) -> None:
        """Assign every *.read permission to the user (e.g. for new users)."""
        read_names = self.list_read_permission_names()
        for name in read_names:
            perm = self.db.query(Permission).filter(Permission.name == name).first()
            if not perm:
                continue
            existing = (
                self.db.query(UserPermission)
                .filter(
                    UserPermission.user_id == user_id,
                    UserPermission.permission_id == perm.id,
                )
                .first()
            )
            if not existing:
                self.db.add(UserPermission(user_id=user_id, permission_id=perm.id))
        self.db.commit()

    def assign_permission(self, user_id: int, permission_name: str) -> None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        permission = self.db.query(Permission).filter(Permission.name == permission_name).first()
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found",
            )
        
        existing = self.db.query(UserPermission).filter(
            UserPermission.user_id == user_id,
            UserPermission.permission_id == permission.id,
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission already assigned",
            )
        
        user_permission = UserPermission(user_id=user_id, permission_id=permission.id)
        self.db.add(user_permission)
        self.db.commit()
    
    def remove_permission(self, user_id: int, permission_name: str) -> None:
        permission = self.db.query(Permission).filter(Permission.name == permission_name).first()
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found",
            )
        
        user_permission = self.db.query(UserPermission).filter(
            UserPermission.user_id == user_id,
            UserPermission.permission_id == permission.id,
        ).first()
        
        if not user_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not assigned to user",
            )
        
        self.db.delete(user_permission)
        self.db.commit()
    
    def user_has_permission(self, user_id: int, permission_name: str) -> bool:
        permission = self.db.query(Permission).filter(Permission.name == permission_name).first()
        if not permission:
            return False
        
        user_permission = self.db.query(UserPermission).filter(
            UserPermission.user_id == user_id,
            UserPermission.permission_id == permission.id,
        ).first()
        
        return user_permission is not None
