from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.job import JobResponse

class SavedJobResponse(BaseModel):
    id: str
    user_id: str
    job_id: str
    created_at: datetime
    job: Optional[JobResponse] = None

    model_config = ConfigDict(from_attributes=True)

class ApplicationCreate(BaseModel):
    job_id: str
    status: str = "Applied" # Not Applied, Applied, Assessment, Interview, Offer, Rejected
    notes: Optional[str] = None
    applied_date: Optional[datetime] = None

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: str
    user_id: str
    job_id: str
    status: str
    applied_date: Optional[datetime] = None
    notes: Optional[str] = None
    updated_at: datetime
    job: Optional[JobResponse] = None

    model_config = ConfigDict(from_attributes=True)

