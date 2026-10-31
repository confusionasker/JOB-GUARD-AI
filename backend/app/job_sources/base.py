from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class JobSourceAdapter(ABC):
    """
    Abstract Base Class for modular Job Ingestion Adapters.
    Follows Open-Closed Principle: new platforms (LinkedIn, Indeed, Career Feeds)
    can be integrated without modifying the core ingestion engine.
    """
    def __init__(self, name: str, is_configured: bool = True):
        self.name = name
        self.is_configured = is_configured

    @abstractmethod
    def search_jobs(self, query: Optional[str] = None, location: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search and retrieve raw job listings from the underlying feed or API."""
        pass

    @abstractmethod
    def get_job_details(self, source_job_id: str) -> Optional[Dict[str, Any]]:
        """Fetch full details for a single job listing."""
        pass

    @abstractmethod
    def normalize_job(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert source-specific raw data into standard Normalized Job Schema."""
        pass

    def is_available(self) -> bool:
        """Indicate whether this adapter is operational and permitted."""
        return self.is_configured

