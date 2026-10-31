from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

class RiskSignalSchema(BaseModel):
    type: str
    severity: str
    message: str

class VerificationSignalsSchema(BaseModel):
    domain_valid: Optional[bool] = None
    free_email: Optional[bool] = None
    domain_match: Optional[bool] = None
    payment_demanded: Optional[bool] = None
    whatsapp_only: Optional[bool] = None
    salary_realistic: Optional[bool] = None

class RiskAnalysisResponse(BaseModel):
    risk_score: int
    risk_level: str
    signals: List[RiskSignalSchema] = []
    verification_signals: Dict[str, Any] = {}
    ml_confidence: Optional[float] = None
    rule_score: Optional[int] = None
    explanation: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

