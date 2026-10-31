from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import Profile
from app.models.risk import JobRiskAnalysis
from app.services.match_engine import match_engine
from app.services.llm_provider import llm_provider

class RecommendEngine:
    @staticmethod
    def rank_and_recommend_jobs(
        db: Session,
        jobs: List[Job],
        resume: Optional[Resume],
        profile: Optional[Profile] = None
    ) -> List[Dict[str, Any]]:
        """
        Evaluate and rank job listings.
        High-risk jobs (risk_score >= 70) are flagged and excluded from top recommended slots.
        """
        evaluated_jobs = []

        for job in jobs:
            # Match scoring
            match_res = match_engine.match_resume_to_job(resume, job, profile)
            match_score = match_res["match_score"]

            # Risk scoring
            risk_record = job.risk_analysis
            risk_score = risk_record.risk_score if risk_record else 15
            risk_level = risk_record.risk_level if risk_record else "Low Risk"

            # Assign recommendation label
            if risk_score >= 70:
                rec_label = "REVIEW RISK"
                # Substantial safety penalty in rank calculation
                rank_score = (match_score * 0.4) - 50.0
            elif match_score >= 82 and risk_score <= 25:
                rec_label = "HIGHLY RECOMMENDED"
                rank_score = match_score + (100 - risk_score) * 0.15
            elif match_score >= 70 and risk_score <= 45:
                rec_label = "GOOD MATCH"
                rank_score = match_score + (100 - risk_score) * 0.1
            elif match_score >= 50 and risk_score <= 65:
                rec_label = "POSSIBLE MATCH"
                rank_score = match_score
            else:
                rec_label = "LOW MATCH"
                rank_score = match_score * 0.8

            evaluated_jobs.append({
                "job": job,
                "match": match_res,
                "risk": {
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "signals": risk_record.signals if risk_record else [],
                    "verification_signals": risk_record.verification_signals if risk_record else {},
                    "explanation": risk_record.explanation if risk_record else ""
                },
                "recommendation_label": rec_label,
                "rank_score": rank_score,
                "ai_explanation": None
            })

        # Sort descending by rank_score (highest safe matches first)
        evaluated_jobs.sort(key=lambda x: x["rank_score"], reverse=True)

        # Generate personalized explanations for top recommendations (sub-second fast)
        for item in evaluated_jobs[:15]:
            j = item["job"]
            m = item["match"]
            r = item["risk"]
            explanation = llm_provider._generate_deterministic_explanation(
                job_title=j.title,
                company=j.company,
                matched_skills=m["matched_skills"],
                missing_skills=m["missing_skills"],
                match_score=m["match_score"],
                risk_score=r["risk_score"],
                risk_level=r["risk_level"]
            )
            item["ai_explanation"] = explanation

        return evaluated_jobs

recommend_engine = RecommendEngine()

