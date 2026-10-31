from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.risk import RiskAnalysisResponse

class MatchResultSchema(BaseModel):
    match_score: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    experience_match: bool = True
    education_match: bool = True
    semantic_score: float = 0.0

class JobBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = "Remote"
    remote_type: Optional[str] = "Onsite"
    description: str
    skills: List[str] = []
    experience_min: Optional[float] = None
    experience_max: Optional[float] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = "USD"
    source: Optional[str] = "Direct"
    job_url: Optional[str] = None
    posted_date: Optional[datetime] = None
    recruiter_email: Optional[str] = None
    company_domain: Optional[str] = None

class JobResponse(JobBase):
    id: str
    is_seed: bool = False
    is_saved: Optional[bool] = False
    risk: Optional[RiskAnalysisResponse] = None
    match: Optional[MatchResultSchema] = None
    recommendation_label: Optional[str] = None
    ai_explanation: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class JobSearchResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    page: int
    limit: int

class VerifyUrlRequest(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None

