
"""Transaction categorizer using TF-IDF + LinearSVC with calibration."""

import json
import os
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix
)
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from scipy.sparse import hstack

from app.config import settings


CATEGORIES = [
    "Food & Dining",
    "Groceries",
    "Transport",
    "Shopping",
    "Bills & Utilities",
    "Rent & Housing",
    "Entertainment & Subscriptions",
    "Health",
    "Education",
    "Travel",
    "Investments & Savings",
    "Income",
    "Other",
]


class TransactionCategorizer:
    """ML-based transaction categorizer using TF-IDF and LinearSVC."""

    def __init__(self):
        """Initialize the categorizer, loading model if available."""
        self.model: Optional[Pipeline] = None
        self.categories = CATEGORIES
        self._load_model()

    def _load_model(self) -> None:
        """Load the trained model from disk if available."""
        if os.path.exists(settings.ML_MODEL_PATH):
            try:
                self.model = joblib.load(settings.ML_MODEL_PATH)
            except Exception:
                self.model = None

    def train(
        self,
        data_path: Optional[str] = None,
        user_corrections: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Train the categorizer model.

        Args:
            data_path: Path to the CSV training data file.
            user_corrections: Optional list of dicts with 'description' and 'category'.

        Returns:
            Dictionary with training metrics.
        """
        data_path = data_path or settings.TRAINING_DATA_PATH

        # Load training data
        df = pd.read_csv(data_path)
        df = df[["description", "category"]].dropna()

        # Append user corrections if provided
        if user_corrections:
            corrections_df = pd.DataFrame(user_corrections)
            # Weight user corrections by duplicating them (3x)
            corrections_df = pd.concat([corrections_df] * 3, ignore_index=True)
            df = pd.concat([df, corrections_df], ignore_index=True)

        # Filter to known categories
        df = df[df["category"].isin(self.categories)]

        X = df["description"].values
        y = df["category"].values

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Build pipeline: TF-IDF (word + char n-grams) -> LinearSVC -> Calibration
        tfidf = TfidfVectorizer(
            max_features=15000,
            ngram_range=(1, 2),
            sublinear_tf=True,
            analyzer="word",
            strip_accents="unicode",
            token_pattern=r"(?u)\b\w+\b",
        )

        # Add character-level features
        tfidf_char = TfidfVectorizer(
            max_features=10000,
            analyzer="char_wb",
            ngram_range=(2, 4),
            sublinear_tf=True,
        )

        # Transform with both word and char TF-IDF
        X_train_word = tfidf.fit_transform(X_train)
        X_test_word = tfidf.transform(X_test)
        X_train_char = tfidf_char.fit_transform(X_train)
        X_test_char = tfidf_char.transform(X_test)

        X_train_combined = hstack([X_train_word, X_train_char])
        X_test_combined = hstack([X_test_word, X_test_char])

        # Train LinearSVC with calibration for probability estimates
        base_svc = LinearSVC(
            class_weight="balanced",
            max_iter=10000,
            C=1.0,
            random_state=42,
        )
        calibrated_svc = CalibratedClassifierCV(base_svc, cv=3)
        calibrated_svc.fit(X_train_combined, y_train)

        # Evaluate
        y_pred = calibrated_svc.predict(X_test_combined)
        accuracy = accuracy_score(y_test, y_pred)

        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        cm = confusion_matrix(y_test, y_pred, labels=self.categories).tolist()

        # Save model components
        model_data = {
            "tfidf_word": tfidf,
            "tfidf_char": tfidf_char,
            "classifier": calibrated_svc,
        }

        os.makedirs(os.path.dirname(settings.ML_MODEL_PATH), exist_ok=True)
        joblib.dump(model_data, settings.ML_MODEL_PATH)

        # Build per-class metrics
        per_class = {}
        for cat in self.categories:
            if cat in report:
                per_class[cat] = {
                    "precision": round(report[cat]["precision"], 4),
                    "recall": round(report[cat]["recall"], 4),
                    "f1_score": round(report[cat]["f1-score"], 4),
                    "support": int(report[cat]["support"]),
                }

        # Save metrics
        metrics = {
            "accuracy": round(accuracy, 4),
            "per_class_metrics": per_class,
            "confusion_matrix": cm,
            "feature_count": X_train_combined.shape[1],
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "total_samples": len(df),
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "categories": self.categories,
        }

        with open(settings.ML_METRICS_PATH, "w") as f:
            json.dump(metrics, f, indent=2)

        # Reload model
        self.model = model_data

        return metrics

    def predict(self, description: str) -> Dict[str, Any]:
        """Predict the category for a transaction description.

        Args:
            description: The transaction description text.

        Returns:
            Dict with category, confidence, alternatives, and needs_review flag.
        """
        if self.model is None:
            self._load_model()
        if self.model is None:
            return {
                "category": "Other",
                "confidence": 0.0,
                "alternatives": [],
                "needs_review": True,
            }

        tfidf_word = self.model["tfidf_word"]
        tfidf_char = self.model["tfidf_char"]
        classifier = self.model["classifier"]

        X_word = tfidf_word.transform([description])
        X_char = tfidf_char.transform([description])
        X = hstack([X_word, X_char])

        predicted_category = classifier.predict(X)[0]
        probabilities = classifier.predict_proba(X)[0]

        # Get class labels
        classes = classifier.classes_

        # Sort by probability descending
        sorted_indices = np.argsort(probabilities)[::-1]

        confidence = float(probabilities[sorted_indices[0]])

        # Top 3 alternatives (excluding the top prediction)
        alternatives = []
        for i in sorted_indices[1:4]:
            alternatives.append({
                "category": classes[i],
                "confidence": round(float(probabilities[i]), 4),
            })

        return {
            "category": predicted_category,
            "confidence": round(confidence, 4),
            "alternatives": alternatives,
            "needs_review": confidence < 0.60,
        }

    def get_metrics(self) -> Optional[Dict[str, Any]]:
        """Load and return the saved model metrics."""
        if os.path.exists(settings.ML_METRICS_PATH):
            with open(settings.ML_METRICS_PATH, "r") as f:
                return json.load(f)
        return None


# Singleton instance
categorizer = TransactionCategorizer()

