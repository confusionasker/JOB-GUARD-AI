import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text, JSON, Boolean, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    # MySQL InnoDB friendly column lengths for composite indexing
    title = Column(String(190), nullable=False, index=True)
    company = Column(String(190), nullable=False, index=True)
    location = Column(String(100), nullable=True, index=True)
    remote_type = Column(String(50), default="Onsite", index=True) # Remote, Hybrid, Onsite
    description = Column(Text, nullable=False)
    skills = Column(JSON, default=list) # List of extracted / required skill strings
    experience_min = Column(Float, nullable=True)
    experience_max = Column(Float, nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    source = Column(String(100), default="Direct", index=True)
    source_job_id = Column(String(190), nullable=True)
    job_url = Column(String(1024), nullable=True)
    posted_date = Column(DateTime, default=datetime.utcnow, nullable=True)
    recruiter_email = Column(String(190), nullable=True)
    company_domain = Column(String(190), nullable=True)
    is_seed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    source_references = relationship("JobSourceReference", back_populates="job", cascade="all, delete-orphan")
    risk_analysis = relationship("JobRiskAnalysis", back_populates="job", uselist=False, cascade="all, delete-orphan")
    matches = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")
    saved_by = relationship("SavedJob", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("JobApplication", back_populates="job", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_job_search", "title", "company", "location"),
    )

class JobSourceReference(Base):
    __tablename__ = "job_source_references"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    source = Column(String(100), nullable=False)
    source_job_id = Column(String(190), nullable=True)
    source_url = Column(String(1024), nullable=True)
    ingested_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    job = relationship("Job", back_populates="source_references")
