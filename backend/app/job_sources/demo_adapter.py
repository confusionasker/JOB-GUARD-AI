import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.job_sources.base import JobSourceAdapter

DEMO_JOBS_RAW: List[Dict[str, Any]] = [
    {
        "id": "demo-001",
        "title": "Senior Python Backend Developer",
        "company": "CloudMatrix Systems",
        "location": "San Francisco, CA",
        "remote_type": "Hybrid",
        "description": "CloudMatrix Systems is seeking a Senior Python Backend Developer to scale our event-driven microservices. You will design high-throughput REST APIs using FastAPI and PostgreSQL, optimize Redis caching, and deploy containerized services on AWS using Docker and Kubernetes. Requirements: 5+ years with Python, deep knowledge of SQL, FastAPI/Django, and CI/CD pipelines.",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes", "AWS", "Redis", "Git", "REST API", "CI/CD"],
        "experience_min": 5.0,
        "experience_max": 9.0,
        "salary_min": 140000.0,
        "salary_max": 175000.0,
        "currency": "USD",
        "recruiter_email": "careers@cloudmatrix.io",
        "company_domain": "cloudmatrix.io",
        "job_url": "https://careers.cloudmatrix.io/jobs/senior-python-dev",
        "posted_days_ago": 2,
    },
    {
        "id": "demo-002",
        "title": "Full Stack Engineer (React & Node.js)",
        "company": "FinVerve Technologies",
        "location": "New York, NY",
        "remote_type": "Remote",
        "description": "FinVerve Tech builds modern financial tooling for modern enterprises. We are looking for a versatile Full Stack Engineer to build responsive dashboards with React, TypeScript, and Tailwind CSS, backed by Node.js and PostgreSQL. Experience with Docker, automated testing, and REST APIs is required.",
        "skills": ["React", "TypeScript", "Node.js", "JavaScript", "PostgreSQL", "Docker", "Tailwind CSS", "REST API", "Git"],
        "experience_min": 3.0,
        "experience_max": 6.0,
        "salary_min": 120000.0,
        "salary_max": 150000.0,
        "currency": "USD",
        "recruiter_email": "talent@finverve.com",
        "company_domain": "finverve.com",
        "job_url": "https://finverve.com/careers/fullstack-engineer",
        "posted_days_ago": 4,
    },
    {
        "id": "demo-003",
        "title": "Machine Learning Engineer",
        "company": "Nova AI Labs",
        "location": "Boston, MA",
        "remote_type": "Hybrid",
        "description": "Join our AI research team deploying production NLP and computer vision models. You will train models using PyTorch, scikit-learn, and Hugging Face Transformers, package inferences as FastAPI microservices, and deploy on GCP Kubernetes clusters. Minimum 3 years in Machine Learning and Python required.",
        "skills": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "scikit-learn", "NLP", "FastAPI", "Docker", "Kubernetes", "Google Cloud"],
        "experience_min": 3.0,
        "experience_max": 7.0,
        "salary_min": 150000.0,
        "salary_max": 190000.0,
        "currency": "USD",
        "recruiter_email": "hr@nova-ailabs.com",
        "company_domain": "nova-ailabs.com",
        "job_url": "https://nova-ailabs.com/jobs/ml-engineer",
        "posted_days_ago": 1,
    },
    {
        "id": "demo-004",
        "title": "Junior Python / Django Developer",
        "company": "Nexus Softworks",
        "location": "Austin, TX",
        "remote_type": "Onsite",
        "description": "Nexus Softworks is hiring an enthusiastic Junior Python Developer! Ideal role for freshers and early-career developers. You will collaborate on web backends with Django and MySQL, write clean unit tests, and maintain Git repositories. Mentorship and technical growth provided.",
        "skills": ["Python", "Django", "SQL", "MySQL", "Git", "REST API", "HTML5", "CSS3"],
        "experience_min": 0.0,
        "experience_max": 2.0,
        "salary_min": 70000.0,
        "salary_max": 85000.0,
        "currency": "USD",
        "recruiter_email": "jobs@nexussoftworks.com",
        "company_domain": "nexussoftworks.com",
        "job_url": "https://nexussoftworks.com/careers/junior-python",
        "posted_days_ago": 5,
    },
    {
        "id": "demo-005",
        "title": "Frontend React Developer",
        "company": "PulseUI Studios",
        "location": "Seattle, WA",
        "remote_type": "Remote",
        "description": "PulseUI Studios crafts next-gen component systems and web applications. We are seeking a talented React developer proficient with Next.js, TypeScript, Redux, and Tailwind CSS. You will translate Figma mockups into accessible, high-performance web components.",
        "skills": ["React", "TypeScript", "Next.js", "Redux", "Tailwind CSS", "JavaScript", "HTML5", "CSS3", "Git"],
        "experience_min": 2.0,
        "experience_max": 5.0,
        "salary_min": 105000.0,
        "salary_max": 130000.0,
        "currency": "USD",
        "recruiter_email": "recruiting@pulseui.design",
        "company_domain": "pulseui.design",
        "job_url": "https://pulseui.design/jobs/react-dev",
        "posted_days_ago": 3,
    },
    {
        "id": "demo-006",
        "title": "Data Entry & Python Assistant (Review Flag)",
        "company": "Apex Global Solutions",
        "location": "Chicago, IL",
        "remote_type": "Remote",
        "description": "Apex Global is seeking a remote assistant to run Python automation scripts and update records. Flexible hours. Contact recruiter via email for swift onboarding.",
        "skills": ["Python", "SQL"],
        "experience_min": 0.0,
        "experience_max": 1.0,
        "salary_min": 45000.0,
        "salary_max": 55000.0,
        "currency": "USD",
        "recruiter_email": "apexrecruiter928@gmail.com", # Risk signal: Free email representing corporate company
        "company_domain": "apexsolutions-sample.org",
        "job_url": "https://apexsolutions-sample.org/apply",
        "posted_days_ago": 6,
    },
    {
        "id": "demo-007",
        "title": "IMMEDIATE JOINING: Remote Python Specialist - High Salary",
        "company": "Global FastTrack Placement",
        "location": "Remote",
        "remote_type": "Remote",
        "description": "Guaranteed job placement! Urgent requirement for Python Developer. Earn huge money from home. Immediate joining with no technical interview required. Selected candidates will be assigned daily automation tasks immediately.",
        "skills": ["Python"],
        "experience_min": 0.0,
        "experience_max": 1.0,
        "salary_min": 120000.0, # Unrealistic fresher salary
        "salary_max": 160000.0,
        "currency": "USD",
        "recruiter_email": "fasttrackhiring@yahoo.com",
        "company_domain": "fasttrack-now.net",
        "job_url": "https://fasttrack-now.net/apply",
        "posted_days_ago": 1,
    },
    {
        "id": "demo-008",
        "title": "CRITICAL SCAM: Work From Home Data Specialist (Upfront Fee)",
        "company": "International Premier Hiring",
        "location": "Remote",
        "remote_type": "Remote",
        "description": "100% Guaranteed Job! Earn $5,000 weekly from day one. No interview required and immediate appointment letter issued. To confirm your application and security clearance, candidate must pay a refundable registration charge of $150 and training deposit via UPI or wire transfer before interview. Limited seats available, pay immediately to secure position.",
        "skills": ["Python", "SQL"],
        "experience_min": 0.0,
        "experience_max": 0.0,
        "salary_min": 240000.0,
        "salary_max": 300000.0,
        "currency": "USD",
        "recruiter_email": "hr.internationalpremier@gmail.com",
        "company_domain": "international-sample-fraud.com",
        "job_url": "https://international-sample-fraud.com/urgent",
        "posted_days_ago": 1,
    }
]

class DemoJobAdapter(JobSourceAdapter):
    """
    Standard Demo Source providing high-fidelity seed listings
    spanning legitimate corporate roles, fresher openings, and known scam edge-cases.
    """
    def __init__(self):
        super().__init__(name="DemoJobAdapter", is_configured=True)

    def search_jobs(self, query: Optional[str] = None, location: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        results = []
        for raw in DEMO_JOBS_RAW:
            if query:
                q = query.lower()
                matches_title = q in raw["title"].lower()
                matches_company = q in raw["company"].lower()
                matches_desc = q in raw["description"].lower()
                matches_skill = any(q in s.lower() for s in raw.get("skills", []))
                if not (matches_title or matches_company or matches_desc or matches_skill):
                    continue
            if location and location.lower() != "all":
                loc = location.lower()
                if loc not in raw.get("location", "").lower() and loc not in raw.get("remote_type", "").lower():
                    continue
            
            results.append(self.normalize_job(raw))
            if len(results) >= limit:
                break
        return results

    def get_job_details(self, source_job_id: str) -> Optional[Dict[str, Any]]:
        for raw in DEMO_JOBS_RAW:
            if raw["id"] == source_job_id:
                return self.normalize_job(raw)
        return None

    def normalize_job(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        posted_days = raw.get("posted_days_ago", 0)
        posted_dt = datetime.utcnow() - timedelta(days=posted_days)
        return {
            "title": raw["title"],
            "company": raw["company"],
            "location": raw.get("location", "Remote"),
            "remote_type": raw.get("remote_type", "Onsite"),
            "description": raw["description"],
            "skills": raw.get("skills", []),
            "experience_min": raw.get("experience_min"),
            "experience_max": raw.get("experience_max"),
            "salary_min": raw.get("salary_min"),
            "salary_max": raw.get("salary_max"),
            "currency": raw.get("currency", "USD"),
            "source": "DemoFeed",
            "source_job_id": raw["id"],
            "job_url": raw.get("job_url", ""),
            "posted_date": posted_dt,
            "recruiter_email": raw.get("recruiter_email"),
            "company_domain": raw.get("company_domain"),
            "is_seed": True,
        }

demo_adapter = DemoJobAdapter()

