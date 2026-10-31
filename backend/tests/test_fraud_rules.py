import pytest
from app.services.fraud_engine import fraud_engine

def test_legitimate_job_low_risk():
    result = fraud_engine.analyze_job(
        title="Senior Python Backend Developer",
        company="Stripe",
        description="Build scalable distributed payment infrastructure with Python and PostgreSQL. Standard 401k, health benefits, and equity provided.",
        recruiter_email="jobs@stripe.com",
        company_domain="stripe.com",
        salary_min=150000.0,
        salary_max=180000.0,
        experience_min=5.0
    )
    assert result["risk_score"] <= 25
    assert result["risk_level"] in ["Low Risk", "Moderate Risk"]
    assert result["verification_signals"]["domain_match"] is True
    assert result["verification_signals"]["payment_demanded"] is False

def test_scam_job_high_risk_payment_demand():
    result = fraud_engine.analyze_job(
        title="Immediate Remote Data Entry Specialist",
        company="Global Quick Cash",
        description="100% Guaranteed Job! Earn $5,000 weekly without any interview. Candidate must pay a refundable registration fee of $150 and security deposit via UPI before appointment letter is issued. Pay immediately to secure limited seat.",
        recruiter_email="quickrecruiter@gmail.com",
        company_domain="globalquickcash-fake.org",
        salary_min=250000.0,
        experience_min=0.0
    )
    assert result["risk_score"] >= 75
    assert result["risk_level"] == "High Risk"
    assert result["verification_signals"]["payment_demanded"] is True
    assert result["verification_signals"]["free_email"] is True
    assert any(s["type"] == "payment_request" for s in result["signals"])

def test_recruiter_domain_mismatch_and_free_email():
    result = fraud_engine.analyze_job(
        title="Backend Software Engineer",
        company="Microsoft Corporation",
        description="Looking for an engineer to join our cloud team.",
        recruiter_email="microsoft.recruiting.dept@yahoo.com",
        company_domain="microsoft.com",
        experience_min=2.0
    )
    assert any(s["type"] == "email_domain" for s in result["signals"])
    assert result["verification_signals"]["free_email"] is True

