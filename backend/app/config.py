"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    SECRET_KEY: str = "finsight-dev-secret-key-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    DATABASE_URL: str = "sqlite:///./finsight.db"

    CURRENCY_SYMBOL: str = "₹"
    CURRENCY_CODE: str = "INR"

    LLM_API_KEY: Optional[str] = ""

    ML_MODEL_PATH: str = "ml_artifacts/categorizer_model.joblib"
    ML_METRICS_PATH: str = "ml_artifacts/metrics.json"
    TRAINING_DATA_PATH: str = "ml_artifacts/training_data.csv"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

