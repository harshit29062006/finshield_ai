"""
Application settings for the FinShield backend.

Values are read from environment variables (see .env.example) and fall back to
safe defaults so the project still runs on a teammate's laptop without setup.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# backend/app/config.py -> backend/ -> repo root
BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent

load_dotenv(BACKEND_DIR / ".env")


def _path_setting(env_name: str, default_folder: str) -> Path:
    """Env variable wins, otherwise use the sibling folder in the repo."""
    value = os.getenv(env_name)
    if value:
        return Path(value).expanduser().resolve()
    return REPO_ROOT / default_folder


# --- Database ---------------------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/finshield",
)

# --- Authentication ---------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

# --- Teammate code locations ------------------------------------------------
# Member 2 ships trained .pkl files, Member 4 ships an importable python package.
ML_MODELS_DIR = _path_setting("ML_MODELS_DIR", "member2_ml")
AML_PACKAGE_DIR = _path_setting("AML_PACKAGE_DIR", "member4_aml")

# Which of Member 2's models the API uses for the fraud probability.
# One of: xgboost, random_forest, logistic_regression
ML_MODEL_NAME = os.getenv("ML_MODEL_NAME", "xgboost")

# --- Hybrid risk scoring ----------------------------------------------------
# Final score = ML weight * fraud probability + AML weight * AML score.
ML_WEIGHT = float(os.getenv("ML_WEIGHT", "0.6"))
AML_WEIGHT = float(os.getenv("AML_WEIGHT", "0.4"))

# Same thresholds Member 4 uses, so the two scores stay comparable.
HIGH_RISK_THRESHOLD = float(os.getenv("HIGH_RISK_THRESHOLD", "0.70"))
MEDIUM_RISK_THRESHOLD = float(os.getenv("MEDIUM_RISK_THRESHOLD", "0.40"))

# How many past transactions of the same sender are passed to the AML module.
AML_HISTORY_LIMIT = int(os.getenv("AML_HISTORY_LIMIT", "50"))
