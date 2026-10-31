from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_optional_current_user
from app.models.user import User, Profile
from app.models.job import Job
from app.models.resume import Resume
from app.schemas.job import JobSearchResponse, JobResponse, VerifyUrlRequest
from app.services.job_service import job_service
from app.services.recommend_engine import recommend_engine
from app.services.url_verifier import url_verifier

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/sync-live")
def trigger_live_sync(
    query: Optional[str] = Query(None, description="Optional technology or role search filter"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch real-time active jobs from live public APIs (Remotive and Arbeitnow),
    run fraud risk analysis, and ingest them directly.
    """
    count = job_service.sync_realtime_jobs(db, query=query, limit=15)
    return {
        "status": "success",
        "message": f"Successfully synced {count} real-time live jobs.",
        "ingested_count": count
    }

@router.get("/search", response_model=JobSearchResponse)
def search_jobs(
    keyword: Optional[str] = Query(None, description="Search keyword for title, company, or description"),
    role: Optional[str] = Query(None, description="Target job role"),
    location: Optional[str] = Query(None, description="Location filter"),
    remote_type: Optional[str] = Query(None, description="Work mode (Remote, Hybrid, Onsite)"),
    experience_min: Optional[float] = Query(None, description="Minimum candidate experience"),
    experience_max: Optional[float] = Query(None, description="Maximum candidate experience"),
    max_risk_score: Optional[int] = Query(None, description="Filter jobs below a maximum risk threshold"),
    source: Optional[str] = Query(None, description="Filter by ingestion source"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Search and filter verified jobs with real-time risk scores and personalized match rates."""
    jobs, total = job_service.search_jobs(
        db=db,
        keyword=keyword,
        role=role,
        location=location,
        remote_type=remote_type,
        experience_min=experience_min,
        experience_max=experience_max,
        max_risk_score=max_risk_score,
        source=source,
        page=page,
        limit=limit,
        user=current_user
    )

    return {
        "jobs": jobs,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/recommended", response_model=List[JobResponse])
def get_recommended_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve personalized recommended jobs for the authenticated candidate.
    High-risk scam listings are safely excluded and filtered out.
    """
    existing_count = db.query(Job).filter(Job.is_seed == False).count()
    if existing_count < 10:
        job_service.sync_realtime_jobs(db, query="software", limit=15)

    resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()

    all_jobs = db.query(Job).all()
    ranked_records = recommend_engine.rank_and_recommend_jobs(db, all_jobs, resume, profile)

    # Return top safe recommendations (excluding REVIEW RISK from primary recommendation feed)
    safe_recommendations = [
        r for r in ranked_records if r["recommendation_label"] != "REVIEW RISK"
    ][:15]

    output = []
    for item in safe_recommendations:
        j = item["job"]
        output.append({
            "id": j.id,
            "title": j.title,
            "company": j.company,
            "location": j.location,
            "remote_type": j.remote_type,
            "description": j.description,
            "skills": j.skills,
            "experience_min": j.experience_min,
            "experience_max": j.experience_max,
            "salary_min": j.salary_min,
            "salary_max": j.salary_max,
            "currency": j.currency,
            "source": j.source,
            "job_url": j.job_url,
            "posted_date": j.posted_date,
            "recruiter_email": j.recruiter_email,
            "company_domain": j.company_domain,
            "is_seed": j.is_seed,
            "risk": item["risk"],
            "match": item["match"],
            "recommendation_label": item["recommendation_label"],
            "ai_explanation": item["ai_explanation"],
        })

    return output

@router.post("/verify-url")
def verify_external_job_url(
    req: VerifyUrlRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify an external job URL or manual job description with SSRF protection,
    fraud risk scoring, domain verification, and resume match rate.
    """
    resume = None
    if current_user:
        resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()

    result = url_verifier.verify_job_url_or_text(
        job_url=req.url,
        manual_title=req.title,
        manual_company=req.company,
        manual_description=req.description,
        resume=resume
    )
    return result

@router.get("/{id}", response_model=JobResponse)
def get_job_details(
    id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full details, risk analysis, and resume match for a single job."""
    job_dict = job_service.get_job_by_id(db, id, user=current_user)
    if not job_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job listing not found"
        )
    return job_dict

