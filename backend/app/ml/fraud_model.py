import os
import joblib
from typing import Optional, Tuple
from app.core.logging import logger

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 1. Project root / ml / models
ROOT_ML_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "..", "ml", "models"))
# 2. backend / ml / models
BACKEND_ML_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "ml", "models"))

def find_model_files():
    for candidate_dir in [ROOT_ML_DIR, BACKEND_ML_DIR]:
        m_path = os.path.join(candidate_dir, "fraud_model.joblib")
        v_path = os.path.join(candidate_dir, "vectorizer.joblib")
        if os.path.exists(m_path) and os.path.exists(v_path):
            return m_path, v_path, candidate_dir
    return None, None, ROOT_ML_DIR

class MLFraudModel:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self._load_model()

    def _load_model(self):
        m_path, v_path, checked_dir = find_model_files()
        try:
            if m_path and v_path:
                self.model = joblib.load(m_path)
                self.vectorizer = joblib.load(v_path)
                logger.info(f"ML Fraud Model and TF-IDF Vectorizer loaded successfully from {checked_dir}.")
            else:
                logger.warning(f"ML Fraud Model artifacts not found at {checked_dir}. Operating in rule-based fallback mode.")
        except Exception as e:
            logger.error(f"Error loading ML Fraud Model: {e}. Falling back to rule-based scoring.")
            self.model = None
            self.vectorizer = None

    def predict_fraud_probability(self, text: str) -> Optional[float]:
        """
        Return the model's predicted probability (0.0 to 1.0) that the job is fraudulent.
        Returns None if model is unavailable.
        """
        if not self.model or not self.vectorizer or not text:
            return None

        try:
            text_clean = text.lower()
            vec = self.vectorizer.transform([text_clean])
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(vec)[0]
                return float(probs[1])
            else:
                pred = self.model.predict(vec)[0]
                return 1.0 if pred == 1 else 0.0
        except Exception as e:
            logger.error(f"Error during ML inference: {e}")
            return None

ml_fraud_model = MLFraudModel()
