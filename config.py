import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
QDRANT_STORAGE_DIR = BASE_DIR / "qdrant_storage"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
QDRANT_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

class Settings:
    # App Settings
    PROJECT_NAME: str = "AI Recruitment Assessment System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    BASE_DIR: Path = BASE_DIR
    UPLOAD_DIR: Path = UPLOAD_DIR
    QDRANT_STORAGE_DIR: Path = QDRANT_STORAGE_DIR
    
    # Database (Defaults to SQLite for instant zero-config setup, supports PostgreSQL via env)
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/recruitment.db")
    
    # Vector Database & Embeddings
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION", "candidate_resumes")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Background Tasks
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # Code Execution
    E2B_API_KEY: str = os.getenv("E2B_API_KEY", "")
    CODE_TIMEOUT_SECONDS: int = int(os.getenv("CODE_TIMEOUT_SECONDS", "10"))
    
    # LiteLLM Configuration
    LITELLM_MODEL: str = os.getenv("LITELLM_MODEL", "gpt-4o-mini")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Scoring & Thresholds
    TECH_WEIGHT: float = 0.40
    CODING_WEIGHT: float = 0.40
    COMMUNICATION_WEIGHT: float = 0.20
    
    SHORTLIST_THRESHOLD: float = float(os.getenv("SHORTLIST_THRESHOLD", "70.0"))
    REVIEW_THRESHOLD: float = float(os.getenv("REVIEW_THRESHOLD", "50.0"))
    
    # Fairness Anonymization
    FAIRNESS_MODE: bool = os.getenv("FAIRNESS_MODE", "True").lower() in ("true", "1", "yes")

settings = Settings()
