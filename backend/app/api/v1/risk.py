from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.job import Job
from app.models.risk import JobRiskAnalysis
from app.schemas.risk import RiskAnalysisResponse

router = APIRouter(prefix="/jobs", tags=["Risk Analysis"])

@router.get("/{id}/risk", response_model=RiskAnalysisResponse)
def get_job_risk(
    id: str,
    db: Session = Depends(get_db)
):
    """Retrieve full risk assessment, heuristic signals, and company verification audit for a job."""
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if not job.risk_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk analysis not found for this job"
        )

    return job.risk_analysis

