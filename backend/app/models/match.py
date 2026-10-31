import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Boolean, JSON, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    match_score = Column(Float, nullable=False) # 0 to 100
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    experience_match = Column(Boolean, default=True)
    education_match = Column(Boolean, default=True)
    semantic_score = Column(Float, default=0.0)
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    job = relationship("Job", back_populates="matches")
    user = relationship("User", back_populates="matches")

    __table_args__ = (
        Index("idx_user_job_match", "user_id", "job_id", unique=True),
    )

