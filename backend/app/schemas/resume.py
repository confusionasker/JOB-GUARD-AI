from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

class EducationItem(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None

class ExperienceItem(BaseModel):
    role: Optional[str] = None
    company: Optional[str] = None
    duration: Optional[str] = None
    raw: Optional[str] = None

class ProjectItem(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class StructuredResumeData(BaseModel):
    skills: List[str] = []
    education: List[Dict[str, Any]] = []
    experience: List[Dict[str, Any]] = []
    projects: List[Dict[str, Any]] = []
    certifications: List[str] = []
    job_titles: List[str] = []
    total_experience_years: int = 0

class ResumeUpdateRequest(BaseModel):
    skills: Optional[List[str]] = None
    target_job_roles: Optional[List[str]] = None
    education: Optional[List[Dict[str, Any]]] = None
    total_experience_years: Optional[int] = None

class ResumeResponse(BaseModel):
    id: str
    file_name: str
    file_type: str
    total_experience_years: int
    structured_data: StructuredResumeData
    raw_text_preview: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ResumeAnalysisResponse(BaseModel):
    extracted_skills: List[str]
    total_experience_years: int
    experience_level: str
    top_matched_roles: List[str]
    missing_in_demand_skills: List[str]
    recommended_skills_to_learn: List[str]
    certifications: List[str]

