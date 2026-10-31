import pytest
from app.utils.ssrf_protection import is_safe_url
from app.services.url_verifier import url_verifier

def test_ssrf_protection_blocks_malicious_urls():
    # Loopback
    safe, msg = is_safe_url("http://127.0.0.1:8000/admin")
    assert not safe

    # Localhost
    safe, msg = is_safe_url("http://localhost:5000/internal")
    assert not safe

    # Cloud metadata IP
    safe, msg = is_safe_url("http://169.254.169.254/latest/meta-data/")
    assert not safe

    # Private network
    safe, msg = is_safe_url("http://192.168.1.1/router")
    assert not safe

    # Unsupported schemes
    safe, msg = is_safe_url("file:///etc/passwd")
    assert not safe

def test_manual_text_verification_fallback():
    result = url_verifier.verify_job_url_or_text(
        manual_title="Work From Home Python Typist",
        manual_company="Fake Recruitment Agency",
        manual_description="Earn $4000 weekly guaranteed. No interview needed! Candidate must pay $100 registration fee via UPI."
    )
    assert result["success"] is True
    assert result["risk"]["risk_score"] >= 60
    assert result["risk"]["risk_level"] in ["Suspicious", "High Risk"]
