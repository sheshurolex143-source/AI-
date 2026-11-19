"""Standalone script to train the transaction categorizer model and generate evaluation metrics."""

import os
import sys

# Ensure UTF-8 output encoding on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.ml.categorizer import categorizer
from scripts.generate_sample_data import generate_training_data


def run_training():
    """Execute model training and print summary metrics."""
    data_path = settings.TRAINING_DATA_PATH
    if not os.path.exists(data_path):
        print(f"Training dataset not found at {data_path}. Generating now...")
        generate_training_data(data_path, samples_per_category=280)

    print(f">> Training TF-IDF + LinearSVC Categorizer on {data_path}...")
    metrics = categorizer.train(data_path)

    acc = metrics["accuracy"] * 100
    samples = metrics["total_samples"]
    features = metrics["feature_count"]
    print(f"\n==========================================")
    print(f"[SUCCESS] Model Training Complete!")
    print(f"   Accuracy: {acc:.2f}%")
    print(f"   Total Samples: {samples}")
    print(f"   Extracted Features: {features}")
    print(f"   Artifact: {settings.ML_MODEL_PATH}")
    print(f"   Metrics:  {settings.ML_METRICS_PATH}")
    print(f"==========================================\n")

    return metrics


if __name__ == "__main__":
    run_training()
