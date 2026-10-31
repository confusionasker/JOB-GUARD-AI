import os
import re
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, confusion_matrix, f1_score, precision_score, recall_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "datasets", "sample_jobs.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def preprocess_text(text: str) -> str:
    """Clean text by lowercasing and removing special punctuation noise."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s\$]", " ", text)
    return " ".join(text.split())

def train_and_evaluate():
    print("=" * 60)
    print("JobGuard AI — Fraud Detection Model Training Pipeline")
    print("=" * 60)

    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)
    print(f"Loaded dataset: {len(df)} samples")
    print(f"Class distribution:\n{df['fraudulent'].value_counts(normalize=True).rename({0: 'Genuine', 1: 'Fraudulent'})}\n")

    # Combine text features
    df["combined_text"] = (
        df["title"].fillna("") + " " +
        df["company"].fillna("") + " " +
        df["description"].fillna("")
    ).apply(preprocess_text)

    X = df["combined_text"]
    y = df["fraudulent"]

    # Stratified split to maintain balance
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    # Feature extraction with TF-IDF (unigrams + bigrams)
    vectorizer = TfidfVectorizer(
        max_features=1000,
        ngram_range=(1, 2),
        stop_words="english",
        sublinear_tf=True
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Train Logistic Regression with balanced class weighting
    print("Training Logistic Regression classifier with balanced class weighting...")
    model = LogisticRegression(class_weight="balanced", random_state=42, C=1.0)
    model.fit(X_train_vec, y_train)

    # Evaluate
    y_pred = model.predict(X_test_vec)
    report = classification_report(y_test, y_pred, target_names=["Genuine", "Fraudulent"])
    cm = confusion_matrix(y_test, y_pred)

    print("\n--- Model Evaluation Results ---")
    print(report)
    print("Confusion Matrix:")
    print(cm)
    print(f"F1-Score: {f1_score(y_test, y_pred):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred):.4f}")
    print(f"Recall: {recall_score(y_test, y_pred):.4f}")

    # Save artifacts
    model_path = os.path.join(MODELS_DIR, "fraud_model.joblib")
    vec_path = os.path.join(MODELS_DIR, "vectorizer.joblib")
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vec_path)
    print(f"\nModel saved successfully to: {model_path}")
    print(f"Vectorizer saved successfully to: {vec_path}")
    print("=" * 60)

if __name__ == "__main__":
    train_and_evaluate()

