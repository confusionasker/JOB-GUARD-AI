import re
from typing import Dict, Any, List, Optional
from app.ml.fraud_model import ml_fraud_model
from app.core.logging import logger

FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", 
    "aol.com", "protonmail.com", "zoho.com", "yandex.com"
}

# High-Risk Payment Patterns
PAYMENT_PATTERNS = [
    (r"(?i)\b(?:registration\s+(?:fee|charge|deposit))\b", "The listing requests an upfront registration fee."),
    (r"(?i)\b(?:interview\s+(?:fee|charge))\b", "The listing requires candidates to pay an interview fee."),
    (r"(?i)\b(?:training\s+(?:fee|charge|deposit|cost)\s+(?:before|prior))\b", "The listing demands payment for mandatory training before employment."),
    (r"(?i)\b(?:refundable\s+(?:security\s+)?deposit)\b", "The listing asks for a refundable security deposit."),
    (r"(?i)\b(?:pay\s+via\s+(?:upi|googlepay|phonepe|crypto|wire\s+transfer))\b", "The listing instructs candidates to make direct UPI or wire transfer payments."),
    (r"(?i)\b(?:equipment\s+(?:charge|dispatch\s+fee))\b", "Candidates are asked to pay for equipment dispatch."),
]

# Unrealistic Promises / Urgency Red Flags
URGENCY_PATTERNS = [
    (r"(?i)\b(?:100%?\s+guaranteed\s+job|guaranteed\s+(?:placement|employment))\b", "Guaranteed job placement promises without technical assessment are a common scam tactic."),
    (r"(?i)\b(?:no\s+(?:technical\s+)?interview\s+required|without\s+(?:any\s+)?interview)\b", "Claims no technical interview or screening is necessary for hiring."),
    (r"(?i)\b(?:earn\s+huge\s+money|earn\s+\$?\d+[\d,]*\s+(?:daily|weekly))\b", "Promises unrealistically high immediate daily or weekly income."),
    (r"(?i)\b(?:limited\s+seats|pay\s+immediately|hurry\s+up)\b", "Employs artificial urgency to pressure candidates into hasty payments."),
    (r"(?i)\b(?:immediate\s+appointment\s+letter|direct\s+joining\s+letter)\b", "Offers instant appointment letters prior to genuine candidate evaluations."),
]

# Contact Red Flags
CONTACT_PATTERNS = [
    (r"(?i)\b(?:whatsapp(?:\s+only)?(?:\s+interview)?|contact\s+on\s+whatsapp)\b", "Recruiter exclusively requests WhatsApp communication for official hiring."),
    (r"(?i)\b(?:telegram(?:\s+only)?)\b", "Recruiter directs communication exclusively to anonymous Telegram accounts."),
]

class FraudEngine:
    """
    Hybrid Fraud Detection Engine.
    Combines deterministic heuristic rules, domain verification checks,
    and a machine learning TF-IDF classification model.
    """
    @classmethod
    def analyze_job(
        cls,
        title: str,
        company: str,
        description: str,
        recruiter_email: Optional[str] = None,
        company_domain: Optional[str] = None,
        salary_min: Optional[float] = None,
        salary_max: Optional[float] = None,
        experience_min: Optional[float] = None,
    ) -> Dict[str, Any]:
        signals: List[Dict[str, str]] = []
        rule_score = 0
        text = f"{title} {description}"

        verification_signals = {
            "domain_valid": bool(company_domain),
            "free_email": False,
            "domain_match": True,
            "payment_demanded": False,
            "whatsapp_only": False,
            "salary_realistic": True,
        }

        # 1. Payment-Related Heuristics (High Severity)
        for pattern, message in PAYMENT_PATTERNS:
            if re.search(pattern, text):
                rule_score += 40
                verification_signals["payment_demanded"] = True
                signals.append({
                    "type": "payment_request",
                    "severity": "high",
                    "message": message
                })
                break  # Don't compound duplicate payment rules infinitely

        # 2. Urgency and Guarantee Red Flags
        for pattern, message in URGENCY_PATTERNS:
            if re.search(pattern, text):
                rule_score += 25
                signals.append({
                    "type": "unrealistic_promise",
                    "severity": "medium",
                    "message": message
                })

        # 3. Contact Channel Red Flags
        for pattern, message in CONTACT_PATTERNS:
            if re.search(pattern, text):
                rule_score += 20
                verification_signals["whatsapp_only"] = True
                signals.append({
                    "type": "suspicious_channel",
                    "severity": "medium",
                    "message": message
                })

        # 4. Recruiter Email & Domain Signals
        if recruiter_email:
            email_lower = recruiter_email.lower().strip()
            email_domain = email_lower.split("@")[-1] if "@" in email_lower else ""

            # Check free email domain for corporate entity
            if email_domain in FREE_EMAIL_DOMAINS:
                verification_signals["free_email"] = True
                rule_score += 18
                signals.append({
                    "type": "email_domain",
                    "severity": "medium",
                    "message": f"Recruiter is using a free email provider (@{email_domain}) rather than an official corporate domain."
                })
            
            # Check domain mismatch
            elif company_domain and email_domain:
                clean_comp_domain = company_domain.lower().replace("http://", "").replace("https://", "").replace("www.", "").strip("/")
                if clean_comp_domain and clean_comp_domain not in email_domain and email_domain not in clean_comp_domain:
                    verification_signals["domain_match"] = False
                    rule_score += 15
                    signals.append({
                        "type": "domain_mismatch",
                        "severity": "medium",
                        "message": f"Recruiter domain (@{email_domain}) does not match the company domain ({clean_comp_domain})."
                    })

        # 5. Salary Anomaly (Fresher with exorbitant compensation)
        effective_salary = salary_max or salary_min or 0
        effective_exp = experience_min if experience_min is not None else 0
        if effective_exp <= 1 and effective_salary >= 120000:
            if verification_signals["payment_demanded"] or "guaranteed" in text.lower():
                rule_score += 25
                verification_signals["salary_realistic"] = False
                signals.append({
                    "type": "salary_anomaly",
                    "severity": "high",
                    "message": f"Unrealistic salary (${int(effective_salary):,}/yr) for entry-level experience paired with high-risk signals."
                })

        # Cap rule score at 100
        rule_score = min(rule_score, 100)

        # 6. ML Classifier Prediction
        combined_text = f"{title} {company} {description}"
        ml_prob = ml_fraud_model.predict_fraud_probability(combined_text)

        # 7. Weighted Risk Score Calculation
        if ml_prob is not None:
            # 55% Heuristic Rules + 45% ML Classifier
            ml_scaled = ml_prob * 100
            final_risk = int(round(0.55 * rule_score + 0.45 * ml_scaled))
        else:
            final_risk = rule_score

        # Bound final score between 0 and 100
        final_risk = max(0, min(100, final_risk))

        # Determine Risk Level Category
        if final_risk <= 20:
            risk_level = "Low Risk"
        elif final_risk <= 50:
            risk_level = "Moderate Risk"
        elif final_risk <= 75:
            risk_level = "Suspicious"
        else:
            risk_level = "High Risk"

        # Generate Human Explanation
        explanation = cls._generate_explanation(final_risk, risk_level, signals, verification_signals)

        return {
            "risk_score": final_risk,
            "risk_level": risk_level,
            "signals": signals,
            "verification_signals": verification_signals,
            "ml_confidence": ml_prob,
            "rule_score": rule_score,
            "explanation": explanation
        }

    @staticmethod
    def _generate_explanation(
        risk_score: int,
        risk_level: str,
        signals: List[Dict[str, str]],
        verification_signals: Dict[str, Any]
    ) -> str:
        if risk_score <= 20:
            return "This listing exhibits standard hiring patterns with no upfront fee requests, valid corporate domain signals, and realistic compensation."
        
        elif risk_score <= 50:
            notes = [s["message"] for s in signals]
            return f"Moderate risk detected ({risk_score}/100). Standard verification recommended: " + " ".join(notes)

        elif risk_score <= 75:
            notes = [s["message"] for s in signals]
            return f"Suspicious listing ({risk_score}/100). Proceed with caution: " + " ".join(notes)

        else:
            reasons = [s["message"] for s in signals]
            return f"High risk scam alert ({risk_score}/100)! Multiple scam signatures detected: " + " ".join(reasons)

fraud_engine = FraudEngine()

