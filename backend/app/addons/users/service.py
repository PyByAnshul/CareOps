from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.addons.users.models import User
from app.addons.users.schemas import UserRegister
from app.core.security.hashing import hash_password, verify_password
from app.core.security.jwt import create_access_token


class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserRegister) -> User:
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        hashed_pwd = hash_password(user_data.password)
        
        user = User(
            email=user_data.email,
            hashed_password=hashed_pwd,
            role=user_data.role,
            workspace_id=user_data.workspace_id,
            is_active=True,
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def generate_token(self, user: User) -> str:
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "workspace_id": user.workspace_id
        }
        return create_access_token(token_data)
