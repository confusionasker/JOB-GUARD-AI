from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.job import Job
from app.models.application import SavedJob
from app.schemas.application import SavedJobResponse
from app.services.job_service import job_service

router = APIRouter(prefix="/jobs", tags=["Saved Jobs"])

@router.get("/saved", response_model=List[SavedJobResponse])
def get_saved_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all jobs saved/bookmarked by the current user."""
    saved_records = db.query(SavedJob).filter(SavedJob.user_id == current_user.id).all()
    results = []
    for s in saved_records:
        job_dict = job_service.get_job_by_id(db, s.job_id, user=current_user)
        results.append({
            "id": s.id,
            "user_id": s.user_id,
            "job_id": s.job_id,
            "created_at": s.created_at,
            "job": job_dict
        })
    return results

@router.post("/{id}/save", status_code=status.HTTP_201_CREATED)
def save_job(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bookmark a job opportunity."""
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    existing = db.query(SavedJob).filter(SavedJob.user_id == current_user.id, SavedJob.job_id == id).first()
    if existing:
        return {"message": "Job is already saved", "saved": True}

    saved = SavedJob(user_id=current_user.id, job_id=id)
    db.add(saved)
    db.commit()
    return {"message": "Job saved successfully", "saved": True}

@router.delete("/{id}/save")
def remove_saved_job(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a job from bookmarks."""
    saved = db.query(SavedJob).filter(SavedJob.user_id == current_user.id, SavedJob.job_id == id).first()
    if not saved:
        return {"message": "Job was not in saved list", "saved": False}

    db.delete(saved)
    db.commit()
    return {"message": "Job removed from saved list", "saved": False}

