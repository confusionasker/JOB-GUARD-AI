import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class JobRiskAnalysis(Base):
    __tablename__ = "job_risk_analysis"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    risk_score = Column(Integer, nullable=False) # 0 to 100
    risk_level = Column(String(50), nullable=False) # Low Risk, Moderate Risk, Suspicious, High Risk
    signals = Column(JSON, default=list) # [{type, severity, message}]
    verification_signals = Column(JSON, default=dict) # {domain_valid: true, free_email: false, ...}
    ml_confidence = Column(Float, nullable=True) # ML model output 0.0 - 1.0
    rule_score = Column(Integer, nullable=True)
    explanation = Column(Text, nullable=True)
    analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    job = relationship("Job", back_populates="risk_analysis")

