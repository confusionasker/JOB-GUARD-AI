from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, Profile
from app.schemas.auth import UserRegister, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token

class AuthService:
    @staticmethod
    def register_user(db: Session, data: UserRegister) -> User:
        existing = db.query(User).filter(User.email == data.email.lower().strip()).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists"
            )
        
        hashed = get_password_hash(data.password)
        new_user = User(
            name=data.name.strip(),
            email=data.email.lower().strip(),
            hashed_password=hashed,
            is_active=True
        )
        db.add(new_user)
        db.flush()

        # Create default empty profile linked to user
        profile = Profile(
            user_id=new_user.id,
            full_name=new_user.name
        )
        db.add(profile)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def authenticate_user(db: Session, data: UserLogin) -> str:
        user = db.query(User).filter(User.email == data.email.lower().strip()).first()
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )
        
        token = create_access_token(subject=user.id)
        return token

auth_service = AuthService()

