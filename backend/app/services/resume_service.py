import os
import uuid
import re
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
from app.models.user import User, Profile
from app.models.resume import Resume
from app.services.resume_parser import resume_parser
from app.core.config import settings
from app.core.logging import logger

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "resumes")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
MAX_BYTES = settings.MAX_RESUME_SIZE_MB * 1024 * 1024

INDUSTRY_HIGH_DEMAND_SKILLS = [
    "Docker", "Kubernetes", "AWS", "CI/CD", "PostgreSQL", 
    "FastAPI", "TypeScript", "React", "Redis", "Machine Learning"
]

class ResumeService:
    @staticmethod
    def process_and_save_resume(db: Session, user: User, upload_file: UploadFile) -> Resume:
        filename = upload_file.filename or "resume.pdf"
        _, ext = os.path.splitext(filename.lower())

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file extension '{ext}'. Only .pdf and .docx files are accepted."
            )

        # Sanitize filename to prevent directory traversal
        safe_id = uuid.uuid4().hex
        safe_filename = f"{user.id}_{safe_id}{ext}"
        target_path = os.path.join(UPLOAD_DIR, safe_filename)

        # Read file contents & validate size
        file_bytes = upload_file.file.read()
        if len(file_bytes) > MAX_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Resume file size exceeds maximum limit of {settings.MAX_RESUME_SIZE_MB}MB."
            )

        with open(target_path, "wb") as f:
            f.write(file_bytes)

        # Extract text & parse structured entities
        try:
            raw_text = resume_parser.extract_text_from_file(target_path, ext)
            structured_data = resume_parser.parse_structured_data(raw_text)
        except Exception as e:
            logger.error(f"Failed to parse resume for user {user.id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to parse resume contents: {str(e)}"
            )

        # Persist resume record in database
        total_exp = structured_data.get("total_experience_years", 0)
        resume_record = Resume(
            user_id=user.id,
            file_name=filename,
            file_path=target_path,
            file_type=ext.replace(".", ""),
            raw_text=raw_text,
            structured_data=structured_data,
            total_experience_years=total_exp
        )
        db.add(resume_record)

        # Synchronize User Profile with extracted skills and titles if empty
        profile = db.query(Profile).filter(Profile.user_id == user.id).first()
        if profile:
            extracted_skills = structured_data.get("skills", [])
            if extracted_skills:
                profile.key_skills = ", ".join(extracted_skills)
            
            job_titles = structured_data.get("job_titles", [])
            if job_titles:
                profile.preferred_titles = ", ".join(job_titles[:3])

            if total_exp <= 2:
                profile.experience_level = "Entry"
            elif total_exp <= 5:
                profile.experience_level = "Mid-Level"
            elif total_exp <= 8:
                profile.experience_level = "Senior"
            else:
                profile.experience_level = "Lead"

        db.commit()
        db.refresh(resume_record)
        return resume_record

    @staticmethod
    def get_latest_resume(db: Session, user: User) -> Optional[Resume]:
        return db.query(Resume).filter(Resume.user_id == user.id).order_by(Resume.created_at.desc()).first()

    @staticmethod
    def get_analysis(db: Session, user: User) -> Dict[str, Any]:
        resume = db.query(Resume).filter(Resume.user_id == user.id).order_by(Resume.created_at.desc()).first()
        if not resume or not resume.structured_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resume found for this user. Please upload a resume first."
            )

        data = resume.structured_data
        skills: List[str] = data.get("skills", [])
        certifications: List[str] = data.get("certifications", [])
        job_titles: List[str] = data.get("job_titles", [])
        total_exp = resume.total_experience_years

        # Calculate missing high-demand skills
        current_skills_lower = {s.lower() for s in skills}
        missing_skills = [
            skill for skill in INDUSTRY_HIGH_DEMAND_SKILLS 
            if skill.lower() not in current_skills_lower
        ]

        # Experience level classification
        if total_exp == 0:
            level = "Fresher (0 years)"
        elif total_exp <= 2:
            level = "Junior (1-2 years)"
        elif total_exp <= 5:
            level = "Mid-Level (2-5 years)"
        elif total_exp <= 8:
            level = "Senior (5-8 years)"
        else:
            level = "Lead / Principal (8+ years)"

        # Infer qualified roles from skills & titles, prioritizing user's preferred titles
        profile = db.query(Profile).filter(Profile.user_id == user.id).first()
        user_preferred_roles = []
        if profile and profile.preferred_titles:
            user_preferred_roles = [t.strip() for t in profile.preferred_titles.split(",") if t.strip()]

        candidate_roles = list(dict.fromkeys(user_preferred_roles + job_titles))
        if "Python" in skills and "FastAPI" in skills and "Python Backend Developer" not in candidate_roles:
            candidate_roles.append("Python Backend Developer")
        if ("React" in skills or "TypeScript" in skills) and "Frontend Engineer" not in candidate_roles:
            candidate_roles.append("Frontend Engineer")
        if ("Machine Learning" in skills or "PyTorch" in skills) and "Machine Learning Engineer" not in candidate_roles:
            candidate_roles.append("Machine Learning Engineer")
        if ("Docker" in skills or "Kubernetes" in skills) and "DevOps / Cloud Engineer" not in candidate_roles:
            candidate_roles.append("DevOps / Cloud Engineer")

        return {
            "extracted_skills": skills,
            "total_experience_years": total_exp,
            "experience_level": level,
            "top_matched_roles": candidate_roles[:6] or ["Software Engineer"],
            "missing_in_demand_skills": missing_skills[:4],
            "recommended_skills_to_learn": missing_skills[:5],
            "certifications": certifications
        }

    @staticmethod
    def update_resume_data(
        db: Session,
        user: User,
        skills: Optional[List[str]] = None,
        target_job_roles: Optional[List[str]] = None,
        education: Optional[List[Dict[str, Any]]] = None,
        total_experience_years: Optional[int] = None
    ) -> Resume:
        resume = db.query(Resume).filter(Resume.user_id == user.id).order_by(Resume.created_at.desc()).first()
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resume found to update. Please upload a resume first."
            )

        data = dict(resume.structured_data or {})
        if skills is not None:
            data["skills"] = sorted(list(dict.fromkeys([s.strip() for s in skills if s.strip()])))
        if target_job_roles is not None:
            data["job_titles"] = list(dict.fromkeys([r.strip() for r in target_job_roles if r.strip()]))
        if education is not None:
            data["education"] = education
        if total_experience_years is not None:
            data["total_experience_years"] = max(0, total_experience_years)
            resume.total_experience_years = max(0, total_experience_years)

        resume.structured_data = data

        # Keep User Profile synchronized
        profile = db.query(Profile).filter(Profile.user_id == user.id).first()
        if profile:
            if skills is not None:
                profile.key_skills = ", ".join(data["skills"])
            if target_job_roles is not None:
                profile.preferred_titles = ", ".join(data["job_titles"])
            if education is not None and len(data["education"]) > 0:
                first_edu = data["education"][0]
                deg = first_edu.get("degree") or ""
                inst = first_edu.get("institution") or ""
                profile.education = f"{deg} - {inst}".strip(" -")
            if total_experience_years is not None:
                profile.experience_level = "Entry" if total_experience_years <= 2 else "Mid-Level"

        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(resume, "structured_data")
        db.commit()
        db.refresh(resume)
        return resume

    @staticmethod
    def delete_latest_resume(db: Session, user: User) -> bool:
        """Permanently delete candidate's resume and reset profile resume fields."""
        resumes = db.query(Resume).filter(Resume.user_id == user.id).all()
        if not resumes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resume found to delete."
            )

        for r in resumes:
            if r.file_path and os.path.exists(r.file_path):
                try:
                    os.remove(r.file_path)
                except Exception as e:
                    logger.warning(f"Could not remove resume file from disk: {e}")
            db.delete(r)

        # Clear resume data from profile
        profile = db.query(Profile).filter(Profile.user_id == user.id).first()
        if profile:
            profile.key_skills = None
            profile.preferred_titles = None
            profile.education = None
            profile.experience_level = "Entry"

        db.commit()
        return True

resume_service = ResumeService()

