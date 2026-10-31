from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from app.models.job import Job, JobSourceReference
from app.models.risk import JobRiskAnalysis
from app.models.resume import Resume
from app.models.user import User, Profile
from app.models.application import SavedJob
from app.job_sources.remotive_adapter import remotive_adapter
from app.job_sources.arbeitnow_adapter import arbeitnow_adapter
from app.job_sources.india_job_adapter import india_job_adapter
from app.utils.deduplication import find_duplicate_job
from app.services.fraud_engine import fraud_engine
from app.services.match_engine import match_engine
from app.services.recommend_engine import recommend_engine
from app.core.logging import logger

class JobService:
    @classmethod
    def purge_seed_jobs(cls, db: Session):
        """Purge any legacy mock/seed jobs so only real-time listings are present."""
        try:
            db.query(Job).filter(Job.is_seed == True).delete()
            db.commit()
        except Exception:
            db.rollback()

    @classmethod
    def sync_realtime_jobs(cls, db: Session, query: Optional[str] = None, limit: int = 15) -> int:
        """
        Fetch genuine, live job opportunities from real-time open APIs (Remotive and Arbeitnow),
        run fraud risk analysis, and persist them into the database.
        """
        logger.info(f"Triggering real-time live sync for query='{query}'...")
        ingested = 0

        # Query live public APIs and India verified tech career feed
        adapters = [india_job_adapter, remotive_adapter, arbeitnow_adapter]
        for adapter in adapters:
            try:
                live_jobs = adapter.search_jobs(query=query, limit=limit)
                for raw in live_jobs:
                    cls.ingest_single_job(db, raw)
                    ingested += 1
            except Exception as e:
                logger.error(f"Error fetching from {adapter.name}: {e}")

        logger.info(f"Real-time sync complete: ingested {ingested} live opportunities.")
        return ingested

    @classmethod
    def ingest_single_job(cls, db: Session, job_dict: Dict[str, Any]) -> Job:
        """
        Normalize, deduplicate, run real-time fraud risk analysis, and persist a live job.
        If duplicate is detected, records a source reference to prevent duplicate UI cards.
        """
        title = job_dict.get("title", "")
        company = job_dict.get("company", "")
        description = job_dict.get("description", "")
        job_url = job_dict.get("job_url")
        source = job_dict.get("source", "RealTime")
        source_job_id = job_dict.get("source_job_id")

        # 1. Deduplication Check
        existing_dup = find_duplicate_job(db, title, company, description, job_url)
        if existing_dup:
            ref = JobSourceReference(
                job_id=existing_dup.id,
                source=source,
                source_job_id=source_job_id,
                source_url=job_url
            )
            db.add(ref)
            db.commit()
            return existing_dup

        # 2. Run Real-Time Fraud Analysis
        risk_res = fraud_engine.analyze_job(
            title=title,
            company=company,
            description=description,
            recruiter_email=job_dict.get("recruiter_email"),
            company_domain=job_dict.get("company_domain"),
            salary_min=job_dict.get("salary_min"),
            salary_max=job_dict.get("salary_max"),
            experience_min=job_dict.get("experience_min"),
        )

        # 3. Create Live Job Record
        new_job = Job(
            title=title,
            company=company,
            location=job_dict.get("location", "Remote"),
            remote_type=job_dict.get("remote_type", "Remote"),
            description=description,
            skills=job_dict.get("skills", []),
            experience_min=job_dict.get("experience_min"),
            experience_max=job_dict.get("experience_max"),
            salary_min=job_dict.get("salary_min"),
            salary_max=job_dict.get("salary_max"),
            currency=job_dict.get("currency", "USD"),
            source=source,
            source_job_id=source_job_id,
            job_url=job_url,
            posted_date=job_dict.get("posted_date"),
            recruiter_email=job_dict.get("recruiter_email"),
            company_domain=job_dict.get("company_domain"),
            is_seed=False
        )
        db.add(new_job)
        db.flush()

        # 4. Attach Live Risk Analysis Record
        risk_record = JobRiskAnalysis(
            job_id=new_job.id,
            risk_score=risk_res["risk_score"],
            risk_level=risk_res["risk_level"],
            signals=risk_res["signals"],
            verification_signals=risk_res["verification_signals"],
            ml_confidence=risk_res["ml_confidence"],
            rule_score=risk_res["rule_score"],
            explanation=risk_res["explanation"]
        )
        db.add(risk_record)

        # 5. Attach Source Reference
        if source:
            ref = JobSourceReference(
                job_id=new_job.id,
                source=source,
                source_job_id=source_job_id,
                source_url=job_url
            )
            db.add(ref)

        db.commit()
        db.refresh(new_job)
        return new_job

    @classmethod
    def search_jobs(
        cls,
        db: Session,
        keyword: Optional[str] = None,
        role: Optional[str] = None,
        location: Optional[str] = None,
        remote_type: Optional[str] = None,
        experience_min: Optional[float] = None,
        experience_max: Optional[float] = None,
        max_risk_score: Optional[int] = None,
        source: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
        user: Optional[User] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Search and filter live stored jobs with user resume match calculations."""
        # Purge any old seed jobs
        cls.purge_seed_jobs(db)

        # If database has few jobs, automatically fetch live real-time jobs
        existing_count = db.query(Job).filter(Job.is_seed == False).count()
        if existing_count < 10:
            cls.sync_realtime_jobs(db, query=keyword or "software", limit=15)

        def build_query(loc_filter: Optional[str] = location):
            q = db.query(Job).filter(Job.is_seed == False)

            if keyword:
                term = f"%{keyword.strip()}%"
                q = q.filter(
                    or_(
                        Job.title.ilike(term),
                        Job.company.ilike(term),
                        Job.description.ilike(term)
                    )
                )

            if role:
                q = q.filter(Job.title.ilike(f"%{role.strip()}%"))

            if loc_filter and loc_filter.lower() != "all":
                q = q.filter(
                    or_(
                        Job.location.ilike(f"%{loc_filter.strip()}%"),
                        Job.remote_type.ilike(f"%{loc_filter.strip()}%")
                    )
                )

            if remote_type and remote_type.lower() != "all":
                q = q.filter(Job.remote_type.ilike(f"%{remote_type.strip()}%"))

            if experience_min is not None:
                q = q.filter(or_(Job.experience_min == None, Job.experience_min <= experience_min))

            if experience_max is not None:
                q = q.filter(or_(Job.experience_max == None, Job.experience_max >= experience_max))

            if source and source.lower() != "all":
                q = q.filter(Job.source.ilike(f"%{source.strip()}%"))

            if max_risk_score is not None:
                q = q.join(JobRiskAnalysis).filter(JobRiskAnalysis.risk_score <= max_risk_score)

            return q

        query = build_query(location)
        total_count = query.count()

        # If keyword search returned 0 results from DB, trigger live real-time query
        if total_count == 0 and keyword:
            cls.sync_realtime_jobs(db, query=keyword, limit=15)
            query = build_query(location)
            total_count = query.count()

            # Smart fallback: if city filter produced 0 results for this company/keyword,
            # surface the company's verified openings across other locations instead of an empty screen
            if total_count == 0 and location and location.lower() != "all":
                fallback_query = build_query("all")
                if fallback_query.count() > 0:
                    query = fallback_query
                    total_count = fallback_query.count()

        # Pagination
        offset = (page - 1) * limit
        jobs = query.order_by(desc(Job.posted_date)).offset(offset).limit(limit).all()

        # Fetch candidate active resume & saved jobs if authenticated
        resume = None
        saved_job_ids = set()
        profile = None

        if user:
            resume = db.query(Resume).filter(Resume.user_id == user.id).order_by(desc(Resume.created_at)).first()
            profile = db.query(Profile).filter(Profile.user_id == user.id).first()
            saved_records = db.query(SavedJob.job_id).filter(SavedJob.user_id == user.id).all()
            saved_job_ids = {r[0] for r in saved_records}

        formatted = []
        for j in jobs:
            match_res = match_engine.match_resume_to_job(resume, j, profile)
            risk = j.risk_analysis

            formatted.append({
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
                "is_seed": False,
                "is_saved": j.id in saved_job_ids,
                "risk": {
                    "risk_score": risk.risk_score if risk else 15,
                    "risk_level": risk.risk_level if risk else "Low Risk",
                    "signals": risk.signals if risk else [],
                    "verification_signals": risk.verification_signals if risk else {},
                    "explanation": risk.explanation if risk else ""
                },
                "match": match_res,
            })

        return formatted, total_count

    @classmethod
    def get_job_by_id(cls, db: Session, job_id: str, user: Optional[User] = None) -> Optional[Dict[str, Any]]:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        resume = None
        is_saved = False
        profile = None

        if user:
            resume = db.query(Resume).filter(Resume.user_id == user.id).order_by(desc(Resume.created_at)).first()
            profile = db.query(Profile).filter(Profile.user_id == user.id).first()
            saved = db.query(SavedJob).filter(SavedJob.user_id == user.id, SavedJob.job_id == job.id).first()
            is_saved = bool(saved)

        match_res = match_engine.match_resume_to_job(resume, job, profile)
        risk = job.risk_analysis

        return {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "remote_type": job.remote_type,
            "description": job.description,
            "skills": job.skills,
            "experience_min": job.experience_min,
            "experience_max": job.experience_max,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "currency": job.currency,
            "source": job.source,
            "job_url": job.job_url,
            "posted_date": job.posted_date,
            "recruiter_email": job.recruiter_email,
            "company_domain": job.company_domain,
            "is_seed": False,
            "is_saved": is_saved,
            "risk": {
                "risk_score": risk.risk_score if risk else 15,
                "risk_level": risk.risk_level if risk else "Low Risk",
                "signals": risk.signals if risk else [],
                "verification_signals": risk.verification_signals if risk else {},
                "explanation": risk.explanation if risk else ""
            },
            "match": match_res,
        }

job_service = JobService()
