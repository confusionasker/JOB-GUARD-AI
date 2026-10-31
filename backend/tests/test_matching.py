import pytest
from app.services.match_engine import match_engine
from app.models.resume import Resume
from app.models.job import Job

def test_resume_job_matching():
    # Mock Resume
    mock_resume = Resume(
        id="res-123",
        user_id="user-123",
        file_name="resume.pdf",
        file_type="pdf",
        total_experience_years=5,
        structured_data={
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
            "education": [{"degree": "Bachelor of Science", "year": "2019"}],
            "total_experience_years": 5
        },
        raw_text="Experienced Senior Backend Python Developer proficient in FastAPI, PostgreSQL, Docker, and Git."
    )

    # Mock Job
    mock_job = Job(
        id="job-123",
        title="Python Backend Developer",
        company="TechCorp",
        description="Looking for a Python Backend Developer with experience in Python, FastAPI, PostgreSQL, and AWS.",
        skills=["Python", "FastAPI", "PostgreSQL", "AWS"],
        experience_min=4.0,
        experience_max=8.0,
        remote_type="Remote"
    )

    match_res = match_engine.match_resume_to_job(mock_resume, mock_job)

    assert match_res["match_score"] >= 75.0
    assert "Python" in match_res["matched_skills"]
    assert "FastAPI" in match_res["matched_skills"]
    assert "PostgreSQL" in match_res["matched_skills"]
    assert "AWS" in match_res["missing_skills"]
    assert match_res["experience_match"] is True
    assert match_res["education_match"] is True

