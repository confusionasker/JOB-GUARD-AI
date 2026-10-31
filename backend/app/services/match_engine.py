import math
from typing import Dict, Any, List, Optional, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models.resume import Resume
from app.models.job import Job
from app.models.user import Profile
from app.core.config import settings
from app.core.logging import logger

class MatchEngine:
    def __init__(self):
        self._sentence_transformer = None
        self._init_embedder()

    def _init_embedder(self):
        try:
            from sentence_transformers import SentenceTransformer
            self._sentence_transformer = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("SentenceTransformer (all-MiniLM-L6-v2) loaded successfully.")
        except Exception:
            logger.info("SentenceTransformer not installed or offline; using TF-IDF semantic cosine similarity.")
            self._sentence_transformer = None

    def calculate_semantic_similarity(self, text_a: str, text_b: str) -> float:
        """Calculate semantic similarity (0.0 to 1.0) between resume and job description."""
        if not text_a or not text_b:
            return 0.0

        if self._sentence_transformer:
            try:
                embeddings = self._sentence_transformer.encode([text_a, text_b])
                cos_sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
                return max(0.0, min(1.0, float(cos_sim)))
            except Exception as e:
                logger.warning(f"SentenceTransformer encoding failed: {e}. Falling back to TF-IDF.")

        # High-performance TF-IDF sublinear cosine similarity fallback
        try:
            tfidf = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=500)
            matrix = tfidf.fit_transform([text_a, text_b])
            cos_sim = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
            # Scale slightly to match human intuition
            return max(0.0, min(1.0, float(cos_sim * 1.4)))
        except Exception:
            return 0.5

    def match_resume_to_job(
        self,
        resume: Optional[Resume],
        job: Job,
        profile: Optional[Profile] = None
    ) -> Dict[str, Any]:
        """
        Evaluate candidate fit against a job opportunity.
        Returns match_score (0-100), matched_skills, missing_skills,
        experience_match, education_match, and semantic_score.
        """
        # Default baseline if no resume uploaded yet
        if not resume or not resume.structured_data:
            return {
                "match_score": 50.0,
                "matched_skills": [],
                "missing_skills": job.skills or [],
                "experience_match": True,
                "education_match": True,
                "semantic_score": 0.5,
            }

        candidate_skills: Set[str] = set(resume.structured_data.get("skills", []))
        candidate_skills_lower = {s.lower() for s in candidate_skills}

        job_skills: List[str] = job.skills or []
        matched_skills = []
        missing_skills = []

        for req in job_skills:
            if req.lower() in candidate_skills_lower:
                matched_skills.append(req)
            else:
                missing_skills.append(req)

        # 1. Skill Score (45%)
        if job_skills:
            matched_count = len(matched_skills)
            total_job_skills = len(job_skills)
            skill_score = (matched_count / total_job_skills) * 100.0
            # Meaningful match boost when candidate matches multiple technical skills
            if matched_count >= 2:
                skill_score = min(100.0, skill_score + 15.0)
            elif matched_count == 0:
                skill_score = 0.0
        else:
            # Unspecified skill jobs should not score higher than real tech jobs
            skill_score = 15.0

        # 2. Experience Fit (20%)
        candidate_exp = resume.total_experience_years
        job_min_exp = job.experience_min or 0.0
        job_max_exp = job.experience_max or (job_min_exp + 5.0)

        if candidate_exp >= job_min_exp:
            exp_match = True
            if candidate_exp <= job_max_exp + 2:
                exp_score = 100.0
            else:
                exp_score = 85.0
        else:
            exp_match = False
            # Entry / fresher friendly roles (req <= 2y) should be accessible to 0 exp candidates
            if job_min_exp <= 2.0:
                exp_score = 95.0
            else:
                exp_score = max(10.0, 100.0 - (job_min_exp - candidate_exp) * 20.0)

        # 3. Semantic Similarity (15%)
        raw_resume = resume.raw_text or " ".join(candidate_skills)
        semantic_sim = self.calculate_semantic_similarity(raw_resume, job.description)
        semantic_score = semantic_sim * 100.0

        # 4. Education Fit (10%)
        education_match = True
        edu_score = 100.0
        desc_lower = job.description.lower()
        if any(term in desc_lower for term in ["master", "phd", "m.s."]):
            has_master = any("master" in str(e).lower() or "m.s" in str(e).lower() or "m.sc" in str(e).lower() for e in resume.structured_data.get("education", []))
            if not has_master:
                education_match = False
                edu_score = 65.0

        # 5. Location / Regional Alignment (10%)
        location_score = 100.0
        job_loc = (job.location or "").lower() + " " + (job.remote_type or "").lower()
        if profile and profile.preferred_locations and profile.preferred_locations != "Any":
            pref_loc = profile.preferred_locations.lower()
            if pref_loc in job_loc:
                location_score = 100.0
            elif "remote" in job_loc:
                location_score = 90.0
            elif any(hub in job_loc for hub in ["india", "kolkata", "bengaluru", "pune", "hyderabad", "chennai", "mumbai", "delhi"]):
                location_score = 85.0
            else:
                location_score = 40.0
        elif any(hub in job_loc for hub in ["india", "kolkata", "bengaluru", "pune", "hyderabad", "chennai", "mumbai", "delhi", "remote"]):
            location_score = 100.0
        else:
            location_score = 50.0

        # 6. Target Role / Title Boost
        cand_roles = []
        if profile and profile.preferred_titles:
            cand_roles.extend([t.strip().lower() for t in profile.preferred_titles.split(",") if t.strip()])
        if resume and resume.structured_data and resume.structured_data.get("job_titles"):
            cand_roles.extend([t.lower() for t in resume.structured_data.get("job_titles", [])])

        title_boost = 0.0
        job_title_lower = job.title.lower()
        for r in cand_roles:
            if r in job_title_lower or any(word in job_title_lower for word in r.split() if len(word) > 3):
                title_boost = 10.0
                break

        # Weighted Total Score
        final_score = (
            settings.WEIGHT_SKILLS * skill_score +
            settings.WEIGHT_EXPERIENCE * exp_score +
            settings.WEIGHT_SEMANTIC * semantic_score +
            settings.WEIGHT_EDUCATION * edu_score +
            settings.WEIGHT_LOCATION * location_score
        ) + title_boost

        final_score = round(max(0.0, min(100.0, final_score)), 1)

        return {
            "match_score": final_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "experience_match": exp_match,
            "education_match": education_match,
            "semantic_score": round(semantic_sim, 2),
        }

match_engine = MatchEngine()

