import re
import html
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from app.job_sources.base import JobSourceAdapter
from app.services.skill_extractor import skill_extractor
from app.core.logging import logger

REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"

def strip_html_tags(text: str) -> str:
    if not text:
        return ""
    # Unescape HTML entities
    cleaned = html.unescape(text)
    # Remove HTML tags
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    # Normalize whitespace
    return " ".join(cleaned.split())

class RemotiveAdapter(JobSourceAdapter):
    """
    Official Remotive Public Job API Adapter.
    Fetches real-time, active software engineering opportunities from global tech employers.
    """
    def __init__(self):
        super().__init__(name="RemotiveAdapter", is_configured=True)

    def search_jobs(self, query: Optional[str] = None, location: Optional[str] = None, limit: int = 25) -> List[Dict[str, Any]]:
        params = {
            "category": "software-dev",
            "limit": limit
        }
        if query and query.strip():
            params["search"] = query.strip()

        try:
            logger.info(f"Querying Remotive Real-Time API with params: {params}")
            with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                res = client.get(REMOTIVE_API_URL, params=params)

            if res.status_code != 200:
                logger.warning(f"Remotive API returned status {res.status_code}")
                return []

            data = res.json()
            raw_jobs = data.get("jobs", [])
            logger.info(f"Remotive Real-Time API returned {len(raw_jobs)} live jobs.")

            normalized = []
            for raw in raw_jobs[:limit]:
                norm = self.normalize_job(raw)
                if norm:
                    normalized.append(norm)
            return normalized

        except Exception as e:
            logger.error(f"Error fetching real-time jobs from Remotive API: {e}")
            return []

    def get_job_details(self, source_job_id: str) -> Optional[Dict[str, Any]]:
        return None

    def normalize_job(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        title = raw.get("title", "").strip()
        company = raw.get("company_name", "").strip()
        if not title or not company:
            return None

        clean_desc = strip_html_tags(raw.get("description", ""))
        skills = skill_extractor.extract_skills(f"{title} {' '.join(raw.get('tags', []))} {clean_desc}")

        # Parse publication date
        pub_date_str = raw.get("publication_date")
        posted_date = datetime.utcnow()
        if pub_date_str:
            try:
                # e.g. "2024-03-15T12:00:00"
                posted_date = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00")).replace(tzinfo=None)
            except Exception:
                posted_date = datetime.utcnow()

        return {
            "title": title,
            "company": company,
            "location": raw.get("candidate_required_location") or "Remote / Global",
            "remote_type": "Remote",
            "description": clean_desc,
            "skills": skills,
            "experience_min": None,
            "experience_max": None,
            "salary_min": None,
            "salary_max": None,
            "currency": "USD",
            "source": "Remotive API (Live)",
            "source_job_id": str(raw.get("id")),
            "job_url": raw.get("url"),
            "posted_date": posted_date,
            "recruiter_email": None,
            "company_domain": raw.get("company_name", "").lower().replace(" ", "") + ".com",
            "is_seed": False,
        }

remotive_adapter = RemotiveAdapter()

