from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.addons.contacts.models import Partner
from app.addons.contacts.schemas import PartnerCreate, PartnerUpdate
from app.addons.permissions.service import PermissionService
from app.addons.users.models import User
from app.core.security.hashing import hash_password


class ContactService:
    def __init__(self, db: Session):
        self.db = db

    def list_partners(self, workspace_id: int) -> List[Partner]:
        return self.db.query(Partner).filter(Partner.workspace_id == workspace_id).all()

    def get_partner(self, partner_id: int, workspace_id: int) -> Partner:
        partner = self.db.query(Partner).filter(
            Partner.id == partner_id, Partner.workspace_id == workspace_id
        ).first()
        if not partner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")
        return partner

    def create_partner(self, data: PartnerCreate, workspace_id: int) -> Partner:
        partner = Partner(**data.model_dump(), workspace_id=workspace_id)
        self.db.add(partner)
        self.db.commit()
        self.db.refresh(partner)
        return partner

    def update_partner(self, partner_id: int, data: PartnerUpdate, workspace_id: int) -> Partner:
        partner = self.get_partner(partner_id, workspace_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(partner, key, value)
        self.db.commit()
        self.db.refresh(partner)
        return partner

    def grant_portal_access(
        self, partner_id: int, password: str, workspace_id: int, email: Optional[str] = None
    ) -> Partner:
        partner = self.get_partner(partner_id, workspace_id)

        if partner.has_portal_access:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Partner already has portal access",
            )

        # Determine login email: use provided email or existing contact email
        if partner.email:
            login_email = partner.email
        elif email:
            login_email = email
            partner.email = email
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contact has no email. Please provide email and password.",
            )

        existing_user = self.db.query(User).filter(User.email == login_email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = User(
            email=login_email,
            hashed_password=hash_password(password),
            role="staff",
            workspace_id=workspace_id,
            is_active=True,
        )
        self.db.add(user)
        self.db.flush()

        partner.has_portal_access = True
        partner.user_id = user.id

        perm_service = PermissionService(self.db)
        perm_service.assign_default_staff_permissions(user.id)

        self.db.commit()
        self.db.refresh(partner)
        return partner

    def revoke_portal_access(self, partner_id: int, workspace_id: int) -> Partner:
        partner = self.get_partner(partner_id, workspace_id)
        
        if not partner.has_portal_access:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Partner does not have portal access"
            )
        
        if partner.user_id:
            user = self.db.query(User).filter(User.id == partner.user_id).first()
            if user:
                user.is_active = False
        
        partner.has_portal_access = False
        
        self.db.commit()
        self.db.refresh(partner)
        return partner
