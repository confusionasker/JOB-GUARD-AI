from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.job import Job
from app.models.application import JobApplication
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from app.services.job_service import job_service

router = APIRouter(prefix="/applications", tags=["Application Tracker"])

@router.get("", response_model=List[ApplicationResponse])
def get_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all tracked job applications for the candidate."""
    applications = db.query(JobApplication).filter(JobApplication.user_id == current_user.id).order_by(JobApplication.updated_at.desc()).all()
    results = []
    for app in applications:
        job_dict = job_service.get_job_by_id(db, app.job_id, user=current_user)
        results.append({
            "id": app.id,
            "user_id": app.user_id,
            "job_id": app.job_id,
            "status": app.status,
            "applied_date": app.applied_date,
            "notes": app.notes,
            "updated_at": app.updated_at,
            "job": job_dict
        })
    return results

@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    data: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update a tracked job application."""
    job = db.query(Job).filter(Job.id == data.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    existing = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.job_id == data.job_id
    ).first()

    if existing:
        existing.status = data.status
        existing.notes = data.notes or existing.notes
        existing.applied_date = data.applied_date or existing.applied_date
        db.commit()
        db.refresh(existing)
        target_app = existing
    else:
        new_app = JobApplication(
            user_id=current_user.id,
            job_id=data.job_id,
            status=data.status,
            notes=data.notes,
            applied_date=data.applied_date or datetime.utcnow()
        )
        db.add(new_app)
        db.commit()
        db.refresh(new_app)
        target_app = new_app

    job_dict = job_service.get_job_by_id(db, target_app.job_id, user=current_user)
    return {
        "id": target_app.id,
        "user_id": target_app.user_id,
        "job_id": target_app.job_id,
        "status": target_app.status,
        "applied_date": target_app.applied_date,
        "notes": target_app.notes,
        "updated_at": target_app.updated_at,
        "job": job_dict
    }

@router.patch("/{id}", response_model=ApplicationResponse)
def update_application_status(
    id: str,
    data: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update pipeline status or interview notes for a tracked job."""
    app_record = db.query(JobApplication).filter(
        JobApplication.id == id,
        JobApplication.user_id == current_user.id
    ).first()

    if not app_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application record not found"
        )

    if data.status:
        app_record.status = data.status
    if data.notes is not None:
        app_record.notes = data.notes

    db.commit()
    db.refresh(app_record)

    job_dict = job_service.get_job_by_id(db, app_record.job_id, user=current_user)
    return {
        "id": app_record.id,
        "user_id": app_record.user_id,
        "job_id": app_record.job_id,
        "status": app_record.status,
        "applied_date": app_record.applied_date,
        "notes": app_record.notes,
        "updated_at": app_record.updated_at,
        "job": job_dict
    }

