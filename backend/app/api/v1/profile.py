from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User, Profile
from app.schemas.user import ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["User Profile"])

@router.get("", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve the candidate profile for the current user."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id, full_name=current_user.name)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("", response_model=ProfileResponse)
def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update profile preferences, skills, and target roles."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(profile, key, value)
    
    db.commit()
    db.refresh(profile)
    return profile

