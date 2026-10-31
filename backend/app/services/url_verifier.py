import re
import json
import httpx
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from app.utils.ssrf_protection import is_safe_url
from app.services.fraud_engine import fraud_engine
from app.services.skill_extractor import skill_extractor
from app.services.match_engine import match_engine
from app.services.llm_provider import llm_provider
from app.models.resume import Resume
from app.core.logging import logger

MAX_CONTENT_BYTES = 2 * 1024 * 1024  # 2MB

class JobUrlVerifier:
    @classmethod
    def verify_job_url_or_text(
        cls,
        job_url: Optional[str] = None,
        manual_title: Optional[str] = None,
        manual_company: Optional[str] = None,
        manual_description: Optional[str] = None,
        resume: Optional[Resume] = None
    ) -> Dict[str, Any]:
        """
        Verify an external job posting by URL or manually pasted text.
        Executes SSRF safety validation, extracts metadata, evaluates fraud risk,
        and matches against candidate's uploaded resume.
        """
        title = (manual_title or "").strip()
        company = (manual_company or "").strip()
        description = (manual_description or "").strip()
        source_name = "Manual Input"
        company_domain = None

        if job_url:
            parsed = urlparse(job_url)
            domain = parsed.hostname or ""
            source_name = domain.replace("www.", "")
            company_domain = source_name

            # 1. SSRF Safety Validation
            is_safe, error_msg = is_safe_url(job_url)
            if not is_safe:
                return {
                    "success": False,
                    "error": f"Security Check Failed: {error_msg}",
                    "suggestion": "Please paste the job title, company, and description manually below."
                }

            # 2. Permitted / Safe Fetch
            try:
                headers = {
                    "User-Agent": "JobGuardAI/1.0 (Job Safety & Verification Bot)",
                    "Accept": "text/html,application/xhtml+xml,application/json",
                }
                with httpx.Client(timeout=5.0, follow_redirects=True) as client:
                    response = client.get(job_url, headers=headers)

                if response.status_code == 200 and len(response.content) <= MAX_CONTENT_BYTES:
                    html_content = response.text
                    extracted = cls._parse_html_job_metadata(html_content, job_url)
                    title = title or extracted.get("title", "")
                    company = company or extracted.get("company", "")
                    description = description or extracted.get("description", "")
                elif response.status_code in [401, 403, 429]:
                    return {
                        "success": False,
                        "error": f"The platform ({source_name}) restricts automated access (HTTP {response.status_code}). JobGuard AI honors platform restrictions and does not bypass access controls.",
                        "suggestion": "Please copy and paste the job description manually into the text field below for instant safety verification."
                    }
            except Exception as e:
                logger.info(f"Could not fetch URL {job_url}: {e}")
                if not description:
                    return {
                        "success": False,
                        "error": f"Could not retrieve webpage: {str(e)}",
                        "suggestion": "Please paste the job description directly into the manual verification box below."
                    }

        # Validate minimum inputs
        title = title or "Job Opportunity"
        company = company or "Company"
        if not description or len(description.strip()) < 20:
            return {
                "success": False,
                "error": "Insufficient job details to perform fraud analysis.",
                "suggestion": "Please provide at least a brief job description (minimum 20 characters)."
            }

        # 3. Extract skills from description
        skills = skill_extractor.extract_skills(description)

        # 4. Analyze Fraud & Risk Signals
        risk_result = fraud_engine.analyze_job(
            title=title,
            company=company,
            description=description,
            company_domain=company_domain
        )

        # 5. Calculate Resume Match
        # Create a transient lightweight Job proxy object for matching
        class TransientJob:
            def __init__(self, t, c, d, s):
                self.title = t
                self.company = c
                self.description = d
                self.skills = s
                self.experience_min = None
                self.experience_max = None
                self.remote_type = "Any"

        temp_job = TransientJob(title, company, description, skills)
        match_result = match_engine.match_resume_to_job(resume, temp_job)

        # 6. Generate AI Recommendation
        explanation = llm_provider.generate_recommendation_explanation(
            job_title=title,
            company=company,
            matched_skills=match_result["matched_skills"],
            missing_skills=match_result["missing_skills"],
            match_score=match_result["match_score"],
            risk_score=risk_result["risk_score"],
            risk_level=risk_result["risk_level"]
        )

        return {
            "success": True,
            "job": {
                "title": title,
                "company": company,
                "source": source_name,
                "job_url": job_url,
                "description_preview": description[:400] + "..." if len(description) > 400 else description,
                "skills": skills,
            },
            "risk": risk_result,
            "match": match_result,
            "recommendation": {
                "score": match_result["match_score"],
                "explanation": explanation
            }
        }

    @staticmethod
    def _parse_html_job_metadata(html: str, url: str) -> Dict[str, str]:
        """Extract OpenGraph metadata, JSON-LD Schema, or HTML title."""
        metadata = {}

        # 1. Schema.org JobPosting in JSON-LD
        json_ld_matches = re.findall(r'<script[^>]*type=[\'"]application/ld\+json[\'"][^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
        for block in json_ld_matches:
            try:
                data = json.loads(block.strip())
                if isinstance(data, dict) and data.get("@type") == "JobPosting":
                    metadata["title"] = data.get("title", "")
                    if isinstance(data.get("hiringOrganization"), dict):
                        metadata["company"] = data["hiringOrganization"].get("name", "")
                    metadata["description"] = data.get("description", "")
                    return metadata
            except Exception:
                pass

        # 2. OpenGraph Meta Tags
        og_title = re.search(r'<meta[^>]*property=[\'"]og:title[\'"][^>]*content=[\'"]([^\'"]+)[\'"]', html, re.IGNORECASE)
        og_desc = re.search(r'<meta[^>]*property=[\'"]og:description[\'"][^>]*content=[\'"]([^\'"]+)[\'"]', html, re.IGNORECASE)
        og_site = re.search(r'<meta[^>]*property=[\'"]og:site_name[\'"][^>]*content=[\'"]([^\'"]+)[\'"]', html, re.IGNORECASE)

        if og_title:
            metadata["title"] = og_title.group(1).strip()
        if og_desc:
            metadata["description"] = og_desc.group(1).strip()
        if og_site:
            metadata["company"] = og_site.group(1).strip()

        # 3. HTML Title Tag fallback
        if "title" not in metadata:
            title_tag = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            if title_tag:
                clean_title = re.sub(r'<[^>]+>', '', title_tag.group(1)).strip()
                metadata["title"] = clean_title

        return metadata

url_verifier = JobUrlVerifier()

