from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict

class ProfileBase(BaseModel):
    full_name: Optional[str] = None
    preferred_titles: Optional[str] = None
    preferred_locations: Optional[str] = None
    remote_preference: Optional[str] = "Any"
    expected_salary: Optional[int] = None
    experience_level: Optional[str] = "Mid-Level"
    key_skills: Optional[str] = None
    education: Optional[str] = None

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: str
    user_id: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime
    profile: Optional[ProfileResponse] = None

    model_config = ConfigDict(from_attributes=True)
