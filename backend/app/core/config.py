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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
