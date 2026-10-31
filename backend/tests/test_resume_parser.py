import pytest
import io
import uuid
import pymupdf
import httpx
from app.main import app
from app.services.resume_parser import resume_parser

def test_resume_parser_structured_extraction():
    sample_text = """
    Jane Smith
    Senior Software Engineer
    Email: jane.smith@example.com | Phone: 555-0199
    
    Summary:
    Results-driven Software Engineer with 6+ years of experience in backend development and cloud architecture.
    
    Skills:
    Python, FastAPI, Docker, Kubernetes, PostgreSQL, AWS, Git, CI/CD, React
    
    Work Experience:
    Senior Software Engineer at CloudTech Inc (2021 - Present)
    - Architected microservices with FastAPI and PostgreSQL serving 2M users.
    - Automated CI/CD deployments using Docker and Kubernetes on AWS.
    
    Software Engineer at DataCorp (2018 - 2021)
    - Developed REST APIs and data ingestion pipelines in Python.
    
    Education:
    Bachelor of Science in Computer Science (2018)
    
    Certifications:
    AWS Certified Solutions Architect
    """

    data = resume_parser.parse_structured_data(sample_text)
    
    assert "Python" in data["skills"]
    assert "FastAPI" in data["skills"]
    assert "Docker" in data["skills"]
    assert "Senior Software Engineer" in data["job_titles"]
    assert data["total_experience_years"] >= 5
    assert len(data["education"]) > 0
    assert "AWS Certified" in data["certifications"]

@pytest.mark.asyncio
async def test_resume_upload_endpoint():
    # 1. Generate an in-memory PDF using pymupdf
    pdf_doc = pymupdf.open()
    page = pdf_doc.new_page()
    page.insert_text((50, 72), "John Doe\nBackend Developer with 4 years experience in Python, FastAPI, and PostgreSQL.\nAWS Certified")
    pdf_bytes = pdf_doc.tobytes()
    pdf_doc.close()

    email = f"resume_user_{uuid.uuid4().hex[:6]}@example.com"
    password = "SecurePassword123!"

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Register user
        reg_res = await client.post("/api/auth/register", json={"name": "John Doe", "email": email, "password": password})
        assert reg_res.status_code == 201

        # Login
        login_res = await client.post("/api/auth/login", json={"email": email, "password": password})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Upload PDF Resume
        files = {"file": ("john_doe_resume.pdf", pdf_bytes, "application/pdf")}
        upload_res = await client.post("/api/resumes/upload", files=files, headers=headers)
        assert upload_res.status_code == 201
        res_data = upload_res.json()
        assert res_data["file_name"] == "john_doe_resume.pdf"
        assert "Python" in res_data["structured_data"]["skills"]
        assert "PostgreSQL" in res_data["structured_data"]["skills"]

        # Fetch current resume
        curr_res = await client.get("/api/resumes/current", headers=headers)
        assert curr_res.status_code == 200
        assert curr_res.json()["file_name"] == "john_doe_resume.pdf"

        # Fetch resume analysis
        analysis_res = await client.get("/api/resumes/analysis", headers=headers)
        assert analysis_res.status_code == 200
        analysis_data = analysis_res.json()
        assert "Python" in analysis_data["extracted_skills"]
        assert len(analysis_data["recommended_skills_to_learn"]) > 0

        # Update resume skills and target job roles
        update_res = await client.put(
            "/api/resumes/current",
            json={
                "skills": ["Python", "PostgreSQL", "FastAPI", "Docker", "PyTorch"],
                "target_job_roles": ["Machine Learning Engineer", "Backend Developer"]
            },
            headers=headers
        )
        assert update_res.status_code == 200
        updated_data = update_res.json()
        assert "PyTorch" in updated_data["structured_data"]["skills"]
        assert "Machine Learning Engineer" in updated_data["structured_data"]["job_titles"]

        # Delete resume
        del_res = await client.delete("/api/resumes/current", headers=headers)
        assert del_res.status_code == 200
        assert del_res.json()["deleted"] is True

        # Verify 404 after deletion
        after_del = await client.get("/api/resumes/current", headers=headers)
        assert after_del.status_code == 404

