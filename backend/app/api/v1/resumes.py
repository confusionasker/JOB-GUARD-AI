from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.resume import ResumeResponse, ResumeAnalysisResponse, ResumeUpdateRequest
from app.services.resume_service import resume_service

router = APIRouter(prefix="/resumes", tags=["Resume Processing"])

@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and parse candidate resume (.pdf or .docx).
    Extracts canonical tech skills, work experience, education, certifications, and target job titles.
    """
    resume_record = resume_service.process_and_save_resume(db, current_user, file)
    
    # Format response preview
    raw_preview = resume_record.raw_text[:300] + "..." if resume_record.raw_text and len(resume_record.raw_text) > 300 else resume_record.raw_text

    return {
        "id": resume_record.id,
        "file_name": resume_record.file_name,
        "file_type": resume_record.file_type,
        "total_experience_years": resume_record.total_experience_years,
        "structured_data": resume_record.structured_data,
        "raw_text_preview": raw_preview,
        "created_at": resume_record.created_at
    }

@router.get("/current", response_model=ResumeResponse)
def get_current_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve the candidate's latest active parsed resume."""
    resume_record = resume_service.get_latest_resume(db, current_user)
    if not resume_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume has been uploaded yet for this account."
        )

    raw_preview = resume_record.raw_text[:300] + "..." if resume_record.raw_text and len(resume_record.raw_text) > 300 else resume_record.raw_text

    return {
        "id": resume_record.id,
        "file_name": resume_record.file_name,
        "file_type": resume_record.file_type,
        "total_experience_years": resume_record.total_experience_years,
        "structured_data": resume_record.structured_data,
        "raw_text_preview": raw_preview,
        "created_at": resume_record.created_at
    }

@router.get("/analysis", response_model=ResumeAnalysisResponse)
def get_resume_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve skill breakdown, qualified role recommendations, and learning targets."""
    return resume_service.get_analysis(db, current_user)

@router.put("/current", response_model=ResumeResponse)
@router.patch("/current", response_model=ResumeResponse)
def update_current_resume(
    payload: ResumeUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update candidate skills, target job roles, or education details manually.
    Synchronizes immediately with user profile and active recommendation models.
    """
    updated_resume = resume_service.update_resume_data(
        db=db,
        user=current_user,
        skills=payload.skills,
        target_job_roles=payload.target_job_roles,
        education=payload.education,
        total_experience_years=payload.total_experience_years
    )

    raw_preview = updated_resume.raw_text[:300] + "..." if updated_resume.raw_text and len(updated_resume.raw_text) > 300 else updated_resume.raw_text

    return {
        "id": updated_resume.id,
        "file_name": updated_resume.file_name,
        "file_type": updated_resume.file_type,
        "total_experience_years": updated_resume.total_experience_years,
        "structured_data": updated_resume.structured_data,
        "raw_text_preview": raw_preview,
        "created_at": updated_resume.created_at
    }

@router.delete("/current", status_code=status.HTTP_200_OK)
def delete_current_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permanently delete candidate's active resume and reset profile synchronization.
    """
    resume_service.delete_latest_resume(db, current_user)
    return {"message": "Resume deleted successfully.", "deleted": True}

