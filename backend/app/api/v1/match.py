from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User, Profile
from app.models.job import Job
from app.models.resume import Resume
from app.schemas.job import MatchResultSchema
from app.services.match_engine import match_engine

router = APIRouter(prefix="/jobs", tags=["Resume Match"])

@router.get("/{id}/match", response_model=MatchResultSchema)
def get_job_match(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate detailed match metrics between the candidate's resume and a specific job listing."""
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()

    match_result = match_engine.match_resume_to_job(resume, job, profile)
    return match_result

