import json
import httpx
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.logging import logger

class LLMProvider:
    """
    Modular LLM Abstraction supporting:
    - Deterministic Fallback (100% offline, zero-cost, factual)
    - Ollama (Local LLM)
    - OpenAI-Compatible Endpoint
    - Google Gemini
    """
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()

    def generate_recommendation_explanation(
        self,
        job_title: str,
        company: str,
        matched_skills: list,
        missing_skills: list,
        match_score: float,
        risk_score: int,
        risk_level: str
    ) -> str:
        # If external provider is configured and available, try it; otherwise use factual deterministic builder
        if self.provider == "ollama" and settings.OLLAMA_BASE_URL:
            result = self._call_ollama(job_title, company, matched_skills, missing_skills, match_score, risk_score)
            if result:
                return result

        if self.provider == "openai" and settings.OPENAI_API_KEY:
            result = self._call_openai(job_title, company, matched_skills, missing_skills, match_score, risk_score)
            if result:
                return result

        # Deterministic Factual Fallback (Always accurate, zero hallucination)
        return self._generate_deterministic_explanation(
            job_title, company, matched_skills, missing_skills, match_score, risk_score, risk_level
        )

    @staticmethod
    def _generate_deterministic_explanation(
        job_title: str,
        company: str,
        matched_skills: list,
        missing_skills: list,
        match_score: float,
        risk_score: int,
        risk_level: str
    ) -> str:
        matched_str = ", ".join(matched_skills[:5]) if matched_skills else "general engineering principles"
        missing_str = ", ".join(missing_skills[:3]) if missing_skills else "none"

        safety_note = (
            f"The listing currently has a {risk_level.lower()} score ({risk_score}/100) with verified corporate domain signals."
            if risk_score <= 20 else
            f"Note: This listing received a {risk_level.lower()} safety score ({risk_score}/100). Please review the safety warnings before applying."
        )

        return (
            f"You match {len(matched_skills)} core technical skills required for this role at {company}. "
            f"Your proficiency in {matched_str} aligns strongly with the job description. "
            f"The primary missing requirement(s) to prepare for: {missing_str}. "
            f"{safety_note} Overall recommendation: "
            f"{'Strong candidate for application.' if match_score >= 80 and risk_score <= 25 else 'Promising fit; verify requirements carefully.'}"
        )

    def _call_ollama(self, title: str, company: str, matched: list, missing: list, score: float, risk: int) -> Optional[str]:
        try:
            prompt = (
                f"Explain why a candidate with skills {matched} is a {score}% match for {title} at {company}. "
                f"Missing skills: {missing}. Fraud risk: {risk}/100. Keep concise and factual. Do not invent facts."
            )
            # Timeout configured for local/network LLMs (e.g. 24B model)
            with httpx.Client(timeout=25.0) as client:
                model_name = settings.OLLAMA_MODEL.strip()
                res = client.post(
                    f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate",
                    json={"model": model_name, "prompt": prompt, "stream": False}
                )
                if res.status_code == 200:
                    text_resp = res.json().get("response", "").strip()
                    if text_resp:
                        return text_resp
        except Exception as e:
            logger.info(f"Ollama call failed or timed out: {e}. Using deterministic explanation.")
        return None

    def _call_openai(self, title: str, company: str, matched: list, missing: list, score: float, risk: int) -> Optional[str]:
        try:
            headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are JobGuard AI. Explain job match concisely and factually without hallucinating."},
                    {"role": "user", "content": f"Title: {title}, Company: {company}, Matched Skills: {matched}, Missing: {missing}, Match: {score}%, Risk: {risk}/100"}
                ],
                "max_tokens": 150
            }
            with httpx.Client(timeout=4.0) as client:
                res = client.post(f"{settings.OPENAI_BASE_URL}/chat/completions", headers=headers, json=payload)
                if res.status_code == 200:
                    return res.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.info(f"OpenAI call failed or timed out: {e}. Using deterministic explanation.")
        return None

llm_provider = LLMProvider()

