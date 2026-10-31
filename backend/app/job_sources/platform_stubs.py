from typing import List, Dict, Any, Optional
from app.job_sources.base import JobSourceAdapter
from app.core.logging import logger

class LinkedInAdapter(JobSourceAdapter):
    """
    LinkedIn Official API Adapter.
    Requires LinkedIn Talent Solutions API Enterprise credentials.
    Gracefully disabled by default to comply with Terms of Service.
    """
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="LinkedInAdapter", is_configured=bool(api_key))
        self.api_key = api_key

    def search_jobs(self, query: Optional[str] = None, location: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        if not self.is_available():
            logger.info("LinkedIn adapter invoked but disabled: enterprise credentials not configured.")
            return []
        return []

    def get_job_details(self, source_job_id: str) -> Optional[Dict[str, Any]]:
        return None

    def normalize_job(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {}

class NaukriAdapter(JobSourceAdapter):
    """
    Naukri Enterprise Recruiter API Adapter.
    Gracefully disabled by default until official API partner credentials are provided.
    """
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="NaukriAdapter", is_configured=bool(api_key))
        self.api_key = api_key

    def search_jobs(self, query: Optional[str] = None, location: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        if not self.is_available():
            logger.info("Naukri adapter invoked but disabled: enterprise credentials not configured.")
            return []
        return []

    def get_job_details(self, source_job_id: str) -> Optional[Dict[str, Any]]:
        return None

    def normalize_job(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {}

class IndeedAdapter(JobSourceAdapter):
    """
    Indeed Publisher API Adapter.
    Gracefully disabled by default until official publisher credentials are provided.
    """
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="IndeedAdapter", is_configured=bool(api_key))
        self.api_key = api_key

    def search_jobs(self, query: Optional[str] = None, location: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        if not self.is_available():
            logger.info("Indeed adapter invoked but disabled: publisher credentials not configured.")
            return []
        return []

    def get_job_details(self, source_job_id: str) -> Optional[Dict[str, Any]]:
        return None

    def normalize_job(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {}

