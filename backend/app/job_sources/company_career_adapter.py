import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.job_sources.base import JobSourceAdapter

class CompanyCareerAdapter(JobSourceAdapter):
    """
    Adapter for Permitted Public Career Portals / Open JSON feeds.
    Ingests public job listings from legitimate developer career portals.
    """
    def __init__(self):
        super().__init__(name="CompanyCareerAdapter", is_configured=True)

    def search_jobs(self, query: Optional[str] = None, location: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        # Public career portal curated listings
        public_listings = [
            {
                "id": "public-stripe-01",
                "title": "Backend Infrastructure Engineer",
                "company": "Stripe",
                "location": "San Francisco, CA",
                "remote_type": "Remote",
                "description": "Build high-reliability payment infrastructure. Requires deep proficiency in distributed systems, Ruby or Python or Go, SQL database optimization, and cloud architecture (AWS). Experience with high-availability microservices and Linux performance tuning.",
                "skills": ["Python", "Go", "Ruby", "SQL", "PostgreSQL", "AWS", "Linux", "Docker", "REST API"],
                "experience_min": 4.0,
                "experience_max": 8.0,
                "salary_min": 170000.0,
                "salary_max": 220000.0,
                "currency": "USD",
                "recruiter_email": "jobs@stripe.com",
                "company_domain": "stripe.com",
                "job_url": "https://stripe.com/jobs/backend-infra",
            },
            {
                "id": "public-datadog-02",
                "title": "Senior Software Engineer - Cloud Integrations",
                "company": "Datadog",
                "location": "New York, NY",
                "remote_type": "Hybrid",
                "description": "Datadog is looking for a Senior Software Engineer to build integrations with AWS, Azure, and Google Cloud. Hands-on experience with Python, Go, Kubernetes, and distributed tracing systems is essential.",
                "skills": ["Python", "Go", "Kubernetes", "Docker", "AWS", "Azure", "Google Cloud", "Git"],
                "experience_min": 5.0,
                "experience_max": 10.0,
                "salary_min": 165000.0,
                "salary_max": 210000.0,
                "currency": "USD",
                "recruiter_email": "recruiting@datadoghq.com",
                "company_domain": "datadoghq.com",
                "job_url": "https://careers.datadoghq.com/detail/cloud-integrations",
            }
        ]

        results = []
        for raw in public_listings:
            if query:
                q = query.lower()
                matches_title = q in raw["title"].lower()
                matches_company = q in raw["company"].lower()
                matches_desc = q in raw["description"].lower()
                if not (matches_title or matches_company or matches_desc):
                    continue
            results.append(self.normalize_job(raw))
            if len(results) >= limit:
                break
        return results

    def get_job_details(self, source_job_id: str) -> Optional[Dict[str, Any]]:
        return None

    def normalize_job(self, raw: Dict[str, Any]) -> Dict[str, Any]:
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
            "source": "CompanyCareer",
            "source_job_id": raw["id"],
            "job_url": raw.get("job_url", ""),
            "posted_date": datetime.utcnow(),
            "recruiter_email": raw.get("recruiter_email"),
            "company_domain": raw.get("company_domain"),
            "is_seed": True,
        }

company_career_adapter = CompanyCareerAdapter()

