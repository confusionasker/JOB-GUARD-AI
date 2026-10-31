import pytest
from app.services.skill_extractor import skill_extractor

def test_skill_extraction_and_normalization():
    text = """
    Senior Backend Engineer with 5+ years of experience building distributed systems.
    Proficient in Python, FastAPI, Django, and Flask.
    Extensive database experience with Postgres, MongoDB, and Redis caching.
    Deployed containerized services using Docker and k8s on AWS.
    Built automated CI/CD pipelines with Git and GitHub Actions.
    Background in Machine Learning using sklearn and PyTorch for NLP models.
    """

    skills = skill_extractor.extract_skills(text)
    
    # Assert canonical names
    assert "Python" in skills
    assert "FastAPI" in skills
    assert "PostgreSQL" in skills  # "Postgres" -> "PostgreSQL"
    assert "MongoDB" in skills
    assert "Redis" in skills
    assert "Docker" in skills
    assert "Kubernetes" in skills  # "k8s" -> "Kubernetes"
    assert "AWS" in skills
    assert "CI/CD" in skills
    assert "Git" in skills
    assert "scikit-learn" in skills  # "sklearn" -> "scikit-learn"
    assert "PyTorch" in skills
    assert "NLP" in skills
    assert "Machine Learning" in skills

def test_alias_normalization():
    assert skill_extractor.normalize_skill_name("postgres") == "PostgreSQL"
    assert skill_extractor.normalize_skill_name("k8s") == "Kubernetes"
    assert skill_extractor.normalize_skill_name("py") == "Python"
    assert skill_extractor.normalize_skill_name("reactjs") == "React"
    assert skill_extractor.normalize_skill_name("sklearn") == "scikit-learn"

