import re
from difflib import SequenceMatcher
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.models.job import Job, JobSourceReference
from app.core.logging import logger

COMPANY_SUFFIXES = [
    r"\binc\.?\b", r"\bllc\.?\b", r"\bcorp\.?\b", r"\bcorporation\b",
    r"\bltd\.?\b", r"\blimited\b", r"\btechnologies\b", r"\bsystems\b",
    r"\blabs\b", r"\bstudios\b", r"\bgroup\b"
]

def clean_company_name(name: str) -> str:
    cleaned = name.lower().strip()
    for suffix in COMPANY_SUFFIXES:
        cleaned = re.sub(suffix, "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[^\w\s]", "", cleaned)
    return " ".join(cleaned.split())

def clean_job_title(title: str) -> str:
    cleaned = title.lower().strip()
    cleaned = re.sub(r"\b(sr\.?|senior)\b", "senior", cleaned)
    cleaned = re.sub(r"\b(jr\.?|junior)\b", "junior", cleaned)
    cleaned = re.sub(r"[^\w\s]", "", cleaned)
    return " ".join(cleaned.split())

def calculate_text_similarity(a: str, b: str) -> float:
    """Calculate character-level / word-level similarity ratio."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a[:500].lower(), b[:500].lower()).ratio()

def find_duplicate_job(db: Session, title: str, company: str, description: str, job_url: Optional[str] = None) -> Optional[Job]:
    """
    Search database for existing duplicate job based on:
    1. Exact URL match
    2. Normalized Title + Normalized Company + High Description Similarity (> 0.82)
    """
    if job_url:
        exact_url_match = db.query(Job).filter(Job.job_url == job_url).first()
        if exact_url_match:
            return exact_url_match

    norm_company = clean_company_name(company)
    norm_title = clean_job_title(title)

    # Query candidate jobs in same company domain or similar company name
    candidates = db.query(Job).all()
    for candidate in candidates:
        cand_norm_company = clean_company_name(candidate.company)
        if cand_norm_company == norm_company or (norm_company in cand_norm_company or cand_norm_company in norm_company):
            cand_norm_title = clean_job_title(candidate.title)
            # Check title similarity
            title_sim = calculate_text_similarity(cand_norm_title, norm_title)
            if title_sim >= 0.75:
                # Check description overlap
                desc_sim = calculate_text_similarity(candidate.description, description)
                if desc_sim >= 0.80:
                    logger.info(f"Duplicate detected: '{title}' at '{company}' matches existing Job ID {candidate.id} (desc sim: {desc_sim:.2f})")
                    return candidate

    return None

