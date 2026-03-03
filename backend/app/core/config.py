from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Job Application Copilot"
    app_env: str = "dev"
    secret_key: str = "change-me-local-dev"
    access_token_expire_minutes: int = 720

    auth_username: str = "admin"
    auth_password: str = "admin"

    database_url: str = "sqlite:///./copilot.db"
    cors_origins: str = "http://localhost:3000"

    llm_api_base: str | None = None
    llm_api_key: str | None = None
    llm_model: str = "gpt-4o-mini"

    policy_path: str = "../policy.yaml"
    fetch_rate_limit_per_minute: int = 20

    # Email notifications
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    notify_email_to: str | None = None
    notify_score_threshold: float = 80.0

    # Job discovery worker
    discovery_enabled: bool = False
    discovery_search_terms: str = "software engineer"
    discovery_location: str = "remote"
    discovery_greenhouse_companies: str = ""  # comma-separated slugs, e.g. "stripe,notion"
    discovery_lever_companies: str = ""       # comma-separated slugs, e.g. "airbnb,figma"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
