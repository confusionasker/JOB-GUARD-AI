import pytest
from app.utils.deduplication import clean_company_name, clean_job_title, calculate_text_similarity

def test_company_and_title_normalization():
    assert clean_company_name("CloudMatrix Systems Inc.") == "cloudmatrix"
    assert clean_company_name("FinVerve Technologies LLC") == "finverve"
    assert clean_company_name("Nova AI Labs, Corp.") == "nova ai"

    assert clean_job_title("Senior Python Developer") == "senior python developer"
    assert clean_job_title("Sr. Backend Engineer") == "senior backend engineer"

def test_similarity_calculation():
    desc1 = "Looking for a Python Developer proficient in FastAPI and PostgreSQL to build scalable web APIs."
    desc2 = "Seeking a Python Developer proficient in FastAPI and PostgreSQL to build scalable web APIs."
    desc_diff = "Frontend Designer specializing in Figma and CSS animations."

    high_sim = calculate_text_similarity(desc1, desc2)
    low_sim = calculate_text_similarity(desc1, desc_diff)

    assert high_sim >= 0.85
    assert low_sim <= 0.40

