import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="saved_jobs")
    job = relationship("Job", back_populates="saved_by")

    __table_args__ = (
        Index("idx_user_saved_job", "user_id", "job_id", unique=True),
    )

class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="Applied", nullable=False) # Not Applied, Applied, Assessment, Interview, Offer, Rejected
    applied_date = Column(DateTime, default=datetime.utcnow, nullable=True)
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")

    __table_args__ = (
        Index("idx_user_job_application", "user_id", "job_id", unique=True),
    )

