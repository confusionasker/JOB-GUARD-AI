import re
import html
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from app.job_sources.base import JobSourceAdapter
from app.services.skill_extractor import skill_extractor
from app.core.logging import logger

ARBEITNOW_API_URL = "https://www.arbeitnow.com/api/job-board-api"

def strip_html_tags(text: str) -> str:
    if not text:
        return ""
    cleaned = html.unescape(text)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    return " ".join(cleaned.split())

class ArbeitnowAdapter(JobSourceAdapter):
    """
    Arbeitnow Real-Time Job Board API Adapter.
    Pulls live engineering postings from active companies.
    """
    def __init__(self):
        super().__init__(name="ArbeitnowAdapter", is_configured=True)

    def search_jobs(self, query: Optional[str] = None, location: Optional[str] = None, limit: int = 25) -> List[Dict[str, Any]]:
        try:
            logger.info("Querying Arbeitnow Real-Time API...")
            with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                res = client.get(ARBEITNOW_API_URL)

            if res.status_code != 200:
                logger.warning(f"Arbeitnow API returned status {res.status_code}")
                return []

            data = res.json()
            raw_jobs = data.get("data", [])
            logger.info(f"Arbeitnow Real-Time API returned {len(raw_jobs)} live jobs.")

            filtered = []
            for raw in raw_jobs:
                title = raw.get("title", "")
                company = raw.get("company_name", "")
                desc = raw.get("description", "")
                tags = " ".join(raw.get("tags", []))

                if query and query.strip():
                    q = query.lower().strip()
                    if not (q in title.lower() or q in company.lower() or q in desc.lower() or q in tags.lower()):
                        continue

                norm = self.normalize_job(raw)
                if norm:
                    filtered.append(norm)
                    if len(filtered) >= limit:
                        break

            return filtered

        except Exception as e:
            logger.error(f"Error fetching real-time jobs from Arbeitnow API: {e}")
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

        is_remote = raw.get("remote", False)
        remote_type = "Remote" if is_remote else "Onsite"

        return {
            "title": title,
            "company": company,
            "location": raw.get("location") or ("Remote" if is_remote else "Onsite"),
            "remote_type": remote_type,
            "description": clean_desc,
            "skills": skills,
            "experience_min": None,
            "experience_max": None,
            "salary_min": None,
            "salary_max": None,
            "currency": "USD",
            "source": "Arbeitnow API (Live)",
            "source_job_id": raw.get("slug"),
            "job_url": raw.get("url"),
            "posted_date": datetime.utcnow(),
            "recruiter_email": None,
            "company_domain": raw.get("company_name", "").lower().replace(" ", "") + ".com",
            "is_seed": False,
        }

arbeitnow_adapter = ArbeitnowAdapter()

