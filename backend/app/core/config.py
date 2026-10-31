import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "JobGuard AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    DATABASE_URL: str = "sqlite:///./jobguard.db"

    SECRET_KEY: str = "supersecret_jwt_key_jobguard_ai_development_only_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    MAX_RESUME_SIZE_MB: int = 10
    ALLOWED_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]

    LLM_PROVIDER: str = "fallback"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    GEMINI_API_KEY: str = ""

    WEIGHT_SKILLS: float = 0.45
    WEIGHT_EXPERIENCE: float = 0.20
    WEIGHT_SEMANTIC: float = 0.15
    WEIGHT_EDUCATION: float = 0.10
    WEIGHT_LOCATION: float = 0.10

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
            ".env"
        ),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

